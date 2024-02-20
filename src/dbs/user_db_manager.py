# src/dbs/user_db_manager.py

from typing import Optional
from src.dbs.base_db_manager import BaseDBManager
from pymongo.results import InsertOneResult, DeleteResult, UpdateResult
from datetime import datetime

class UserDBManager(BaseDBManager):
    """
    Manages database operations related to users using Motor for asynchronous access.
    """

    async def find_user_by_email(self, email: str) -> Optional[dict]:
        """
        Finds a user document by email asynchronously.

        Parameters:
            email: The email address to search for.

        Returns:
            The user document if found, None otherwise.
        """
        try:
            db_instance = await self.get_db()
            user = await db_instance["users"].find_one({"email": email})
            return user
        except Exception as e:
            self.logger.error(f"Error finding a user by email: {e}")
            raise

    async def insert_user(self, user_data: dict) -> InsertOneResult:
        """
        Inserts a new user document asynchronously.

        Parameters:
            user_data: The user document to insert.

        Returns:
            The inserted ID of the new user.
        """
        try:
            db_instance = await self.get_db()
            result = await db_instance["users"].insert_one(user_data)
            return result
        except Exception as e:
            self.logger.error(f"Error inserting a user: {e}")
            raise

    async def delete_user_by_email(self, email: str) -> DeleteResult:
        """
        Deletes a user document by email.
        
        Parameters:
            email: The email address of the user to delete.
        
        Returns:
            The result of the delete operation.
        
        Raises:
            Exception: If the delete operation fails.
        """
        try:
            db_instance = await self.get_db()
            result = await db_instance["users"].delete_one({"email": email})
            return result
        except Exception as e:
            self.logger.error(f"Error deleting user by email: {e}")
            raise

    async def update_user(self, email: str, update_data: dict) -> UpdateResult:
        """
        Updates a user document.
        
        Parameters:
            email: The email address of the user to update.
            update_data: The data to update in the user's document.
        
        Returns:
            The result of the update operation.
        
        Raises:
            Exception: If the update operation fails.
        """
        try:
            db_instance = await self.get_db()
            result = await db_instance["users"].update_one({"email": email}, {'$set': update_data})
            return result
        except Exception as e:
            self.logger.error(f"Error updating user: {e}")
            raise

    async def update_user_password(self, email: str, hashed_password: str) -> UpdateResult:
        """
        Updates a user's password and refreshes the 'updated_at' timestamp.
        
        Parameters:
            email: The email address of the user whose password is being updated.
            hashed_password: The new hashed password.
        
        Returns:
            The result of the update operation.
        
        Raises:
            Exception: If the password update operation fails.
        """
        try:
            db_instance = await self.get_db()
            current_time = datetime.now()
            result = await db_instance["users"].update_one(
                {"email": email},
                {"$set": {"password": hashed_password, "updated_at": current_time}}
            )
            return result
        except Exception as e:
            self.logger.error(f"Error updating user password: {e}")
            raise

    