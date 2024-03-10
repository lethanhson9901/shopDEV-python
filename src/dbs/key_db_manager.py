# src/dbs/key_db_manager.py

from src.dbs.base_db_manager import BaseDBManager
from datetime import datetime

from datetime import datetime
from src.dbs.base_db_manager import BaseDBManager

class KeyDBManager(BaseDBManager):
    """
    Manages key-related operations in the database.
    """
    
    async def save_key_information(self, user_id: str, refresh_token: str,
                                    public_key: str = None, private_key: str = None) -> bool:
        """
        Updates or inserts key information for a given user, maintaining a bounded list of used refresh tokens.

        Parameters:
        - user_id (str): The unique identifier for the user.
        - refresh_token (str): The most recently issued refresh token.
        - public_key (str, optional): The user's public key.
        - private_key (str, optional): The user's private key.

        Returns:
        - bool: True if the operation is successful, False otherwise.
        """
        try:
            db = await self.get_db()
            result = await db.keys.update_one(
                {"user_id": user_id},
                {"$set": {
                    "refresh_token": refresh_token,
                    "public_key": public_key,
                    "private_key": private_key,
                    "updated_at": datetime.utcnow()
                }},
                upsert=True
            )
            return result.acknowledged
        except Exception as e:
            self.logger.error(f"Error saving key information for user {user_id}: {e}")
            return False

    async def find_key_information(self, user_id: str):
        """
        Retrieves key information for a specific user.

        Parameters:
        - user_id (str): The unique identifier for the user.

        Returns:
        - dict: The key information if found, None otherwise.
        """
        try:
            db = await self.get_db()
            # Ensure to match the user_id as a string, as stored in the database
            key_info = await db.keys.find_one({"user_id": user_id})
            return key_info
        except Exception as e:
            self.logger.error(f"Error retrieving key information for user {user_id}: {e}")
            return None
        
    async def delete_refresh_token(self, user_id: str, refresh_token: str) -> bool:
        """
        Deletes the user's record based on user_id.

        Parameters:
        - user_id (str): The unique identifier for the user to delete.
        - refresh_token (str): The refresh token related to the user. [Note: This parameter is maintained for interface consistency but is not used in the deletion process.]

        Returns:
        - bool: True if the operation is successful, False otherwise.
        """
        try:
            db = await self.get_db()
            # Delete the user's record from the database
            result = await db.keys.delete_one({"user_id": user_id})
            return result.deleted_count > 0
        except Exception as e:
            self.logger.error(f"Error deleting user record for user {user_id}: {e}")
            return False
    
    async def add_refresh_token_to_list(self, user_id: str, refresh_token: str) -> bool:
        """
        Adds a refresh token to the refresh_tokens_used list for a specific user, ensuring the list does not exceed a predefined limit.

        Parameters:
        - user_id (str): The unique identifier for the user.
        - refresh_token (str): The refresh token to add to the list.

        Returns:
        - bool: True if the operation is successful, False otherwise.
        """
        try:
            db = await self.get_db()
            # Define the maximum number of refresh tokens to store
            max_tokens_stored = 10

            # Use MongoDB's $addToSet and $slice to efficiently manage the list size and uniqueness
            result = await db.keys.update_one(
                {"user_id": user_id},
                {
                    "$push": {
                        "refresh_tokens_used": {
                            "$each": [refresh_token],
                            "$slice": -max_tokens_stored
                        }
                    }
                }
            )
            return result.modified_count > 0
        except Exception as e:
            self.logger.error(f"Error adding refresh token for user {user_id}: {e}")
            return False
    
    async def find_by_refresh_token_used(self, refresh_token: str):
        """
        Finds a key record based on a refresh token used.

        Parameters:
        - refresh_token (str): The refresh token to search for in the refresh_tokens_used list.

        Returns:
        - dict: The key record if a matching refresh token is found, None otherwise.
        """
        try:
            db = await self.get_db()
            key_record = await db.keys.find_one({"refresh_tokens_used": refresh_token})
            return key_record
        except Exception as e:
            self.logger.error(f"Error finding key record by refresh token {refresh_token}: {e}")
            return None