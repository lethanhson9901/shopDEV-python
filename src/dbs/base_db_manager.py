# src/dbs/base_db_manager.py
import logging
from typing import Optional
from src.dbs.init_mongodb import Database
from src.helpers.log_config import setup_logger

class BaseDBManager:
    """
    BaseDBManager provides shared functionalities for database operations.
    """
    
    logger = setup_logger()
    
    def __init__(self, db: Optional[Database] = None):
        self._db_instance = db or Database()
        self._db = None
    
    async def get_db(self):
        if self._db is None:
            try:
                self._db = await self._db_instance.get_db()
            except Exception as e:
                self.logger.error(f"Error establishing a database connection: {e}")
                raise
        return self._db

    @staticmethod
    def convert_objectid_to_str(item: dict) -> dict:
        """
        Converts MongoDB ObjectId fields to string for JSON serialization.
        
        Parameters:
            item: The document containing an ObjectId field.
        
        Returns:
            The document with ObjectId fields converted to strings.
        """
        if item and "_id" in item:
            item["_id"] = str(item["_id"])
        return item