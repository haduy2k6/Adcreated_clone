from redis.asyncio import Redis
import pymongo
import json
from bson import ObjectId
from datetime import timedelta
import hashlib
from backend.login.centerDB import get_collection

class RedisConfig:
    _instance = None
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.r_server = None
        async def connectToRedis(self):
            if self.r_server is None:
                self.r_server = Redis(
                    host= 'localhostRedis',
                    port = 6379,
                    db = 0,
                    retry_on_timeout=True,
                    connection_pool=15,
                    max_connections=5,
                    socket_timeout=5,
                    health_check_interval=10
                )
            return self.r_server