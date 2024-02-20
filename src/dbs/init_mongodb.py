# src/dbs/init_mongodb.py

from src.helpers.check_connect import monitor_system_resources
from motor.motor_asyncio import AsyncIOMotorClient
from src.configs.config import CurrentConfig
import asyncio
from src.helpers.log_config import setup_logger

class Database:
    """
    Singleton class for managing the database connection to MongoDB asynchronously.

    Attributes:
        _instance (Database): The singleton instance of the Database class.
        _is_connected (bool): Flag to indicate if the connection to MongoDB is established.
        _lock (asyncio.Lock): Lock for thread-safe operations in asynchronous context.
        logger (logging.Logger): Logger for logging database connection activities.

    Methods:
        get_instance: Class method to get the singleton instance of the Database class.
        connect: Asynchronously establishes a connection to MongoDB.
        disconnect: Asynchronously closes the connection to MongoDB.
        get_db: Returns the database connection if connected, otherwise attempts to connect first.
    """

    _instance = None
    _is_connected = False
    _lock = asyncio.Lock()
    logger = setup_logger()

    @classmethod
    async def get_instance(cls):
        """
        Gets the singleton instance of the Database class, creating it if necessary.

        Returns:
            The singleton instance of the Database class.
        """
        async with cls._lock:
            if cls._instance is None:
                cls._instance = super(Database, cls).__new__(cls)
                cls._instance._init()  # Initialize the instance
            return cls._instance

    def _init(self):
        """Initializes the Database instance; a substitute for __init__."""
        if not hasattr(self, '_initialized'):  # Prevent re-initialization
            self._client = None
            self._db = None
            self._initialized = True

    async def connect(self):
        """
        Asynchronously establishes a connection to MongoDB using the configuration
        specified in CurrentConfig.
        """
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
        """
        Asynchronously closes the MongoDB connection.
        """
        async with self._lock:
            if self._is_connected and self._client is not None:
                self._client.close()
                self._is_connected = False
                self.logger.info("Disconnected from MongoDB")

    async def get_db(self):
        """
        Returns the MongoDB database connection, establishing it if necessary.

        Returns:
            The MongoDB database connection.
        """
        if not self._is_connected:
            await self.connect()
        return self._db

async def start_monitoring():
    """
    Starts the system resource monitoring process asynchronously.
    """
    await monitor_system_resources()
