# src/dbs/init_mongodb.py

from src.helpers.check_connect import monitor_system_resources
from motor.motor_asyncio import AsyncIOMotorClient
from src.configs.config import CurrentConfig  # Ensure this import matches your project structure
import asyncio
from src.helpers.log_config import setup_logger

class Database:
    _instance = None
    _is_connected = False
    _lock = asyncio.Lock()  # Correctly used for async operations
    logger = setup_logger()

    @classmethod
    async def get_instance(cls):
        async with cls._lock:
            if cls._instance is None:
                cls._instance = super(Database, cls).__new__(cls)
                # Initialize it here to avoid recursion with __init__
                cls._instance._init()
            return cls._instance

    def _init(self):
        """A substitute for __init__, to initialize the instance."""
        if not hasattr(self, '_initialized'):  # Prevent reinitialization
            self._client = None
            self._db = None
            self._initialized = True

    async def connect(self):
        async with self._lock:
            if not self._is_connected:
                try:
                    connection_string = CurrentConfig.MONGO_CONNECTION_STRING
                    db_name = CurrentConfig.MONGO_DB_NAME
                    pool_size = CurrentConfig.POOL_SIZE

                    self._client = AsyncIOMotorClient(connection_string, maxPoolSize=pool_size)
                    self._db = self._client[db_name]
                    self._is_connected = True
                    self.logger.info("Connected to MongoDB")
                except Exception as e:
                    self.logger.error(f"Failed to connect to MongoDB: {e}")
                    self._is_connected = False

    async def disconnect(self):
        async with self._lock:
            if self._is_connected and self._client is not None:
                self._client.close()
                self._is_connected = False
                self.logger.info("Disconnected from MongoDB")

    async def get_db(self):
        if not self._is_connected:
            await self.connect()
        return self._db


async def start_monitoring():
    await monitor_system_resources()
