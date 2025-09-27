from pymongo import AsyncMongoClient
import os

class MyDatabase:
    _instance = None
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.client=None
            cls._instance.myDB = None
        return cls._instance
    
    async def connect(self):
        if self.client is None:
            self.client = AsyncMongoClient(
            host="mongodb+srv://collabofduy_db_user:dY8zIM68Vp48iXJX@logindb.yelpph0.mongodb.net/",
            maxPoolSize =30,
            minPoolSize = 3,
            maxConnecting = 3,
            read_preference = "primaryPreferred"
            )
            
            self.myDB = self.client["Login"]
        return self.myDB
    async def collection (self):
        schema = {
            "$jsonSchema":{
                "bsonType":"object",
                "requires": ["email","phone","passwork","role"],
                "properties":{
                    "email":{
                        "bsonType": "string",
                        "pattern": "^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}$",
                        "description": "must be a valid email address and is required"
                    },
                    "phone":{
                        "bsonType":"string",
                        "minLength":9,
                        "maxLength":11,
                        "pattern":"^[0-9][0-9]*[0-9]$"
                    },
                    "passwork":{
                        "bsonType":"string",
                        "pattern": "^(?=.*[A-Z])(?=.*[!@#$%^&*])(?=.*[0-9]).{8,}$",
                    },
                    "info":{
                        "bsonType":"string",
                        "description":" Se duoc ma hoa tat ca thong tin ca nhan thanh 1 string"
                    },
                    "history":{
                        "bsonType":"array",
                        "maxLength":5,
                        "description":" Se duoc ma hoa theo : Id + Ngay thay doi + Thay doi cai gi"
                    },
                    "role":{
                        "bsonType":"string",
                        "enum":["admin","vipMon","vipYear","normal"]
                    }
                }
            }
        }
        return self.myDB.create_collection(
            name="Person",
            validator= schema
            )
async def get_collection():
    mydb = MyDatabase()
    return mydb.collection()