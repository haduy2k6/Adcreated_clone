from redis_Config import RedisConfig
from redis_Read import Read
from tenacity import wait_exponential, stop_after_attempt, retry
import logging

logger = logging.getLogger(__name__)

class Delete:
    def __init__(self):
        self.__redis_config = RedisConfig()
        self.master = None

    async def _ensure_connected(self):
        if self.master is None:
            self.master= await self.__redis_config.connectToRedis()

    @retry(
        stop=stop_after_attempt(2),
        wait=wait_exponential(multiplier=1, min=2, max=8)
    )
    async def logout(self, parameter: dict):
        """
        parameter: {
            jti,
            session_id
        }
        """
        await self._ensure_connected()
        __keys = [
            f"re:{parameter.get('jti')}",
            f"ra:{parameter.get('session_id')}",
            f"s:{parameter.get('session_id')}"
        ]
        __LUA_LOGOUT = """
            redis.call("DEL", KEYS[1])
            redis.call("DEL", KEYS[2])
            redis.call("DEL", KEYS[3])
        """
        script = await self.master.script_load(__LUA_LOGOUT)
        await self.master.evalsha(
            script,
            3,
            *__keys
        )

    @retry(
        stop=stop_after_attempt(2),
        wait=wait_exponential(multiplier=1, min=2, max=6)
    )
    async def del_refresh(self, jti):
        await self._ensure_connected()
        await self.master.delete(f"re:{jti}")

    @retry(
        stop=stop_after_attempt(2),
        wait=wait_exponential(multiplier=1, min=2, max=6)
    )
    async def del_list_oldist(self):
        await self._ensure_connected()
        read_ops = Read()
        __keysOld = await read_ops.read_list_user_oldist()
        if __keysOld:
            await self.master.delete(*__keysOld)