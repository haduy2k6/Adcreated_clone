from login.load_var import Config
from redis.asyncio import Redis, ConnectionPool

class RedisConfig:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.r_master = None
            cls._instance._pool = ConnectionPool(
                host=Config.REDIS_HOST,
                port=Config.REDIS_PORT,
                username=Config.REDIS_USERNAME,
                password=Config.REDIS_PASSWORD,
                decode_responses=True, 
                socket_timeout=5,
                retry_on_timeout=True,
                health_check_interval=10,
                max_connections=8
            )
        return cls._instance

    async def connectToRedis(self):
        try:
            if self.r_master is None:
                self.r_master = Redis(connection_pool=self._pool)
            return self.r_master
        except Exception as e:
            print(f"Kết nối tới Redis thất bại: {e}")
            raise