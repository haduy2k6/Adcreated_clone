
from tenacity import wait_exponential, stop_after_attempt, retry
from redis_Config import RedisConfig
from redis.exceptions import RedisError

class Update:
    def __init__(self):
        self.__redis_config = RedisConfig()
        self.__redis_master = None

    async def _ensure_connected(self):
        if self.__redis_master is None:
            self.__redis_master = await self.__redis_config.connectToRedis()

    @retry(
        stop=stop_after_attempt(2),
        wait=wait_exponential(multiplier=1, min=2, max=4)
    )
    async def update_element(self, element: dict, session_id):
        """
        element: Field need change - new value
        """
        await self._ensure_connected()
        if await self.__redis_master.exists(f"s:{session_id}"):
            listkey = list(element.keys())[0]
            r = await self.__redis_master.hset(f"s:{session_id}", listkey, element[listkey])
            return True if r == 0 else False
        return False
    
    @retry(
        stop=stop_after_attempt(2),
        wait=wait_exponential(multiplier=1, min=2, max=4)
    )
    async def update_multiple_fields(self, fields: dict, session_id):
        """
            Update nhiều fields cùng lúc
            fields: {'email': 'new@example.com', 'name': 'New Name', 'avatar': 'url'}
        """
        await self._ensure_connected()
        
        if await self.__redis_master.exists(f"s:{session_id}"):
            result = await self.__redis_master.hset(
                f"s:{session_id}", 
                mapping=fields
            )
            return True
        return False