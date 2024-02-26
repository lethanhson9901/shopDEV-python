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
            existing_data = await db.keys.find_one({"user_id": user_id}) or {}
            refresh_tokens_used = existing_data.get("refresh_tokens_used", [])
            
            # Limit the size of the refresh tokens list to the latest 10 tokens
            max_tokens_stored = 10
            refresh_tokens_used = refresh_tokens_used[-(max_tokens_stored-1):]
            refresh_tokens_used.append(refresh_token)

            result = await db.keys.update_one(
                {"user_id": user_id},
                {"$set": {
                    "refresh_token": refresh_token,
                    "public_key": public_key,
                    "private_key": private_key,
                    "updated_at": datetime.utcnow()
                },
                 "$push": {
                     "refresh_tokens_used": {
                         "$each": [refresh_token],
                         "$slice": -max_tokens_stored
                     }
                 }},
                upsert=True
            )
            return result.acknowledged
        except Exception as e:
            self.logger.error(f"Error saving key information for user {user_id}: {e}")
            return False

