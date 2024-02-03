# src/dbs/init_mongodb.py
import motor.motor_asyncio
from dotenv import load_dotenv
import os

load_dotenv()  # Take environment variables from .env.

class Database:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Database, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        self._client = None
        self._db = None

    async def connect(self):
        if not self._client or not self._db:
            connection_string = os.getenv('MONGO_CONNECTION_STRING')
            self._client = motor.motor_asyncio.AsyncIOMotorClient(connection_string)
            self._db = self._client['shopDEV']  # Use your database name here.

    async def get_db(self):
        await self.connect()
        return self._db

# To ensure that the database connection is established on application startup,
# you can use the Database.connect() method with FastAPI's event handlers.
