# path/filename: src/dbs/item_db_manager.py

from typing import Optional
from src.dbs.base_db_manager import BaseDBManager
from pymongo.results import InsertOneResult, DeleteResult, UpdateResult
from datetime import datetime
from bson import ObjectId

class ItemDBManager(BaseDBManager):
    """
    Manages database operations related to items using Motor for asynchronous access.
    """

    async def find_item_by_id(self, item_id: str) -> Optional[dict]:
        """
        Finds an item document by its ObjectId asynchronously.

        Parameters:
            item_id: The string representation of the item's ObjectId.

        Returns:
            The item document if found, None otherwise.
        """
        try:
            db_instance = await self.get_db()
            item = await db_instance["items"].find_one({"_id": ObjectId(item_id)})
            return item
        except Exception as e:
            self.logger.error(f"Error finding an item by ID: {e}")
            raise

    async def insert_item(self, item_data: dict) -> InsertOneResult:
        """
        Inserts a new item document asynchronously.

        Parameters:
            item_data: The item document to insert.

        Returns:
            The inserted ID of the new item.
        """
        try:
            db_instance = await self.get_db()
            result = await db_instance["items"].insert_one(item_data)
            return result
        except Exception as e:
            self.logger.error(f"Error inserting an item: {e}")
            raise

    async def delete_item_by_id(self, item_id: str) -> DeleteResult:
        """
        Deletes an item document by its ObjectId.
        
        Parameters:
            item_id: The ObjectId of the item to delete.
        
        Returns:
            The result of the delete operation.
        
        Raises:
            Exception: If the delete operation fails.
        """
        try:
            db_instance = await self.get_db()
            result = await db_instance["items"].delete_one({"_id": ObjectId(item_id)})
            return result
        except Exception as e:
            self.logger.error(f"Error deleting item by ID: {e}")
            raise

    async def update_item(self, item_id: str, update_data: dict) -> UpdateResult:
        """
        Updates an item document.
        
        Parameters:
            item_id: The ObjectId of the item to update.
            update_data: The data to update in the item's document.
        
        Returns:
            The result of the update operation.
        
        Raises:
            Exception: If the update operation fails.
        """
        try:
            db_instance = await self.get_db()
            result = await db_instance["items"].update_one({"_id": ObjectId(item_id)}, {'$set': update_data})
            return result
        except Exception as e:
            self.logger.error(f"Error updating item: {e}")
            raise
