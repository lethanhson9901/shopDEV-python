# src/dbs/init_mongodb.py

import motor.motor_asyncio
from dotenv import load_dotenv
import os
from src.helpers.check_connect import monitor_system_resources

load_dotenv()  # Ideally placed in the entry point of your application

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
                connection_string = os.getenv('MONGO_CONNECTION_STRING')
                db_name = os.getenv('MONGO_DB_NAME', 'shopDEV')  # Default to 'shopDEV'
                self._client = motor.motor_asyncio.AsyncIOMotorClient(connection_string)
                self._db = self._client[db_name]
                self._is_connected = True
                # Consider moving connection count check to a dedicated monitoring or debugging endpoint
            except Exception as e:
                # More specific exception handling can be added here
                print(f"Failed to connect to MongoDB: {e}")
                self._is_connected = False

    async def get_db(self):
        if not self._is_connected:
            await self.connect()
        return self._db

# Function to start the monitoring process
async def start_monitoring():
    await monitor_system_resources()
