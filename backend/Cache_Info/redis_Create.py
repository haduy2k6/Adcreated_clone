import asyncio
import hashlib
from redis_Config import RedisConfig
import json

from tenacity import wait_exponential, stop_after_attempt, retry
from redis.exceptions import RedisError, ResponseError
from redis_Delete import Delete
import logging

logger = logging.getLogger(__name__)

class Create:
    def __init__(self):
        self.__redis_config = RedisConfig()
        self.__redis_master = None

    async def _ensure_connected(self):
        if self.__redis_master is None:
            self.__redis_master = await self.__redis_config.connectToRedis()

    @staticmethod
    async def ultra_short_hash(text, length=8):
        h = hashlib.sha256(text.encode()).hexdigest()
        return h[:length]

    @retry(
        stop=stop_after_attempt(2),
        wait=wait_exponential(multiplier=1, min=2, max=8),
    )
    async def create_refresh_store(self, parameter: dict):
        """
        parameter: List _IP (thong qua blueprint)
        """
        await self._ensure_connected()
        try:
            async with self.__redis_master.pipeline(transaction=True) as pipe:
                pipe.setex(
                    f"re:{parameter.get('jti')}",
                    parameter.get('ttl',3600),
                    json.dumps(parameter)
                )
                await pipe.execute()
        except ResponseError as e:
            if "OOM" in str(e):
                logger.error("Out of memory.")
                raise
        except RedisError as r:
            logger.error("RedisError. Retrying...")
            raise
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            raise

    @retry(
        stop=stop_after_attempt(2),
        wait=wait_exponential(multiplier=1, min=2, max=6)
    )
    async def create_rate_limit(self, parameter: dict):
        """
        parameter: { jti, endpoint: str, limit = 100, ttl = 3600 }
        """
        __LUA_RATE = """
            local key = KEYS[1]
            local limit = tonumber(ARGV[1])
            local create = redis.call("INCR", key)
            if create <= limit and create >= 1 then
                return create
            else
                return 0
            end
        """
        await self._ensure_connected()
        try:
            script_sha = await self.__redis_master.script_load(__LUA_RATE)
            result = await self.__redis_master.evalsha(
                script_sha,
                1,
                f"ra:{parameter.get('session_id')}",  # Fixed: Use session_id instead of jti
                parameter.get('limit', 100)
            )
            if result != 0:
                return True
            else:
                delete_ops = Delete()
                await delete_ops.logout({'jti': parameter.get('jti'), 'session_id': parameter.get('session_id')})
                return False
        except ResponseError as re:
            if 'OOM' in str(re):
                raise
            logger.warning("Script execution error")
            raise
        except Exception as e:
            logger.warning(f"Unknown error: {e}")
            raise

    @retry(
        stop=stop_after_attempt(2),
        wait=wait_exponential(multiplier=1, min=2, max=16)
    )
    async def create_user(self, parameter: dict):
        """
        parameter: {
            'refresh': dict(),
            'session_store': dict()
        }
        """
        await self._ensure_connected()
        session_data = parameter.get("session_store", {})
        refresh_data = parameter.get("refresh", {})
        __LUA_user = """
            -- Create refresh token store
            local refresh_store = redis.call('SETEX', KEYS[1], tonumber(ARGV[1]), ARGV[2])
            -- Rate limiting
            local limit = tonumber(ARGV[3])
            local create = redis.call('INCR', KEYS[2])
            -- Is Active
            redis.call('HSET', KEYS[3], 'status', ARGV[4])
            if create <= limit and create >= 1 then
                return create
            else
                return 0
            end
        """
        try:
            script_sha = getattr(self, '_lua_user_sha', None)
            if not script_sha:
                script_sha = await self.__redis_master.script_load(__LUA_user)
                self._lua_user_sha = script_sha
        except Exception as e:
            logger.warning(f"Failed to load Lua script: {e}")
            return

        k = await Create.ultra_short_hash(session_data.get("email"))
        keys = [
            f"re:{refresh_data.get('jti')}",
            f"ra:{session_data.get('session_id')}",  # Fixed: Use session_id
            k
        ]
        args = [
            str(refresh_data.get('ttl',3600)),
            json.dumps(refresh_data),
            '100',
            session_data.get('session_id')
        ]
        try:
            result = await asyncio.gather(
                self.__redis_master.hset(f"s:{session_data.get('session_id')}", mapping=session_data),
                self.__redis_master.expire(f"s:{session_data.get('session_id')}", 5400)
            )
            if script_sha and result:
                raw_results = await self.__redis_master.evalsha(script_sha, 3, *keys, *args)
                if raw_results == 0:
                    delete_ops = Delete()
                    await delete_ops.logout({'jti': refresh_data.get('jti'), 'session_id': session_data.get('session_id')})
        except ResponseError as e:
            if "OOM" in str(e):
                logger.error("Out of memory.")
                raise
        except Exception as e:
            logger.error(f"This failure is caused by parameter: create_user: {e}")
            return

    @retry(
        stop=stop_after_attempt(2),
        wait=wait_exponential(multiplier=1, min=2, max=16)
    )
    async def create_magiclink(self, token):
        await self._ensure_connected()
        r = await self.__redis_master.setex(token, 300, "")
        return r