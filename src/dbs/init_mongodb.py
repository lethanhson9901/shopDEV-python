# src/dbs/init_mongodb.py

import motor.motor_asyncio
from src.configs.config import CurrentConfig
from src.helpers.check_connect import monitor_system_resources

class Database:
    _instance = None
    _is_connected = False

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Database, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        self._client = None
        self._db = None

    async def connect(self):
        if not self._is_connected:
            try:
                # Use configuration from CurrentConfig
                connection_string = CurrentConfig.MONGO_CONNECTION_STRING
                db_name = CurrentConfig.MONGO_DB_NAME  # Now using CurrentConfig
                pool_size = CurrentConfig.POOL_SIZE  # This is already handled by CurrentConfig
                
                self._client = motor.motor_asyncio.AsyncIOMotorClient(connection_string, maxPoolSize=pool_size)
                self._db = self._client[db_name]
                self._is_connected = True
            except Exception as e:
                print(f"Failed to connect to MongoDB: {e}")
                self._is_connected = False

    async def get_db(self):
        if not self._is_connected:
            await self.connect()
        return self._db

async def start_monitoring():
    await monitor_system_resources()
