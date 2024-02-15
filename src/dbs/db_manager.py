# src/dbs/db_manager.py

import logging
from typing import Optional
from pymongo.results import InsertOneResult, DeleteResult, UpdateResult
from src.dbs.init_mongodb import Database
from src.helpers.log_config import setup_logger

class DBManager:
    # Class-level logger initialization
    logger = setup_logger()

    def __init__(self, db: Optional[Database] = None):
        self._db_instance = db or Database()
        self._db = None  # Will be set when get_db is first called

    async def get_db(self):
        if self._db is None:
            try:
                self._db = await self._db_instance.get_db()
            except Exception as e:
                self.logger.error(f"Error establishing a database connection: {e}")
                raise
        return self._db

    async def find_user_by_email(self, email: str) -> Optional[dict]:
        try:
            db_instance = await self.get_db()
            user = await db_instance["users"].find_one({"email": email})
            return user
        except Exception as e:
            self.logger.error(f"Error finding a user by email: {e}")
            raise

    async def insert_user(self, user_data: dict) -> InsertOneResult:
        try:
            db_instance = await self.get_db()
            result = await db_instance["users"].insert_one(user_data)
            return result
        except Exception as e:
            self.logger.error(f"Error inserting a user: {e}")
            raise

    async def delete_user_by_email(self, email: str) -> DeleteResult:
        try:
            db_instance = await self.get_db()
            result = await db_instance["users"].delete_one({"email": email})
            return result
        except Exception as e:
            self.logger.error(f"Error deleting a user by email: {e}")
            raise

    async def update_user(self, email: str, update_data: dict) -> UpdateResult:
        try:
            db_instance = await self.get_db()
            result = await db_instance["users"].update_one({"email": email}, {'$set': update_data})
            return result
        except Exception as e:
            self.logger.error(f"Error updating a user: {e}")
            raise

    async def update_user_password(self, email: str, hashed_password: str) -> UpdateResult:
        """
        Update the password of a user in the database.

        Parameters:
        - email (str): The email of the user whose password is to be updated.
        - hashed_password (str): The hashed new password to be set for the user.

        Returns:
        - UpdateResult: The result of the update operation.
        """
        try:
            db_instance = await self.get_db()
            result = await db_instance["users"].update_one({"email": email}, {"$set": {"password": hashed_password}})
            return result
        except Exception as e:
            self.logger.error(f"Error updating user password: {e}")
            raise


    @staticmethod
    def convert_objectid_to_str(item: dict) -> dict:
        """Convert ObjectId fields to a string for JSON serialization."""
        if item and "_id" in item:
            item["_id"] = str(item["_id"])
        return item
