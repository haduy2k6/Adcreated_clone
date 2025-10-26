import hashlib
from redis_Config import RedisConfig
from tenacity import wait_exponential, stop_after_attempt, retry
import logging


logger = logging.getLogger(__name__)

class Read:
    def __init__(self):
        self.__redis_config = RedisConfig()
        self.master = None

    async def _ensure_connected(self):
        if self.master is None:
            self.master = await self.__redis_config.connectToRedis()

    @staticmethod
    async def _hash_email(text, length=8):
        h = hashlib.sha256(text.encode()).hexdigest()
        return h[:length]

    @retry(
        stop=stop_after_attempt(2),
        wait=wait_exponential(multiplier=1, min=2, max=8)
    )
    async def read_profile(self, session_id):
        await self._ensure_connected()
        r= await self.master.hgetall(f"s:{session_id}")
        return r

    @retry(
        stop=stop_after_attempt(2),
        wait=wait_exponential(multiplier=1, min=2, max=8)
    )
    async def read_list_user_oldist(self):
        """
        Searches by Action status: isActive or isn't Active in refresh_store
        """
        await self._ensure_connected()
        return [key async for key in self.master.scan_iter(match="Off")]

    @retry(
        stop=stop_after_attempt(2),
        wait=wait_exponential(multiplier=1, min=2, max=8)
    )
    async def read_by_email(self, email):
        await self._ensure_connected()
        hash_key = await self._hash_email(email)
        result = await self.master.hgetall(hash_key)
        if result != {} :
            return await self.read_profile(result.get("status"))
        return {}

    @retry(
        stop=stop_after_attempt(2),
        wait=wait_exponential(multiplier=1, min=2, max=8)
    )
    async def read_magiclink(self, token):
        await self._ensure_connected()
        result = await self.master.exists(token)
        return result if result else -1
    
    @retry(
        stop=stop_after_attempt(2),
        wait=wait_exponential(multiplier=1, min=2, max=8)
    )
    async def read_vertiy_refesh(self,jti):
        await self._ensure_connected()
        result = await self.master.exists(f"re:{jti}")
        return  f"re:{jti}" if result==1  else -1
    
    @retry(
        stop=stop_after_attempt(2),
        wait=wait_exponential(multiplier=1, min=2, max=8)
    )
    async def read_access_token(self,jti):
        # TRich xuat du lieu de tao access token                                                                                                                                                                                    
        success = await self.read_vertiy_refesh(jti)
            
        if not success or success == -1:
            return {}
        vals = self.master.hmget(success, ["sub", "role", "session_id"])
        return vals
