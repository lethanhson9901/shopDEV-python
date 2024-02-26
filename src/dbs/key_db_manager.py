# src/dbs/key_db_manager.py

from src.dbs.base_db_manager import BaseDBManager
from datetime import datetime

class KeyDBManager(BaseDBManager):
    async def save_key_information(self, user_id: str, refresh_token: str, public_key: str = None, private_key: str = None) -> bool:
        try:
            db = await self.get_db()
            # Fetch existing refresh tokens
            existing_data = await db.keys.find_one({"user_id": user_id}) or {}
            refresh_tokens_used = existing_data.get("refresh_tokens_used", [])
            refresh_tokens_used.append(refresh_token)  # Append the new token

            result = await db.keys.update_one(
                {"user_id": user_id},
                {"$set": {
                    "refresh_token": refresh_token,
                    "public_key": public_key,
                    "private_key": private_key,
                    "refresh_tokens_used": refresh_tokens_used,  # Save the updated list
                    "updated_at": datetime.utcnow()
                }},
                upsert=True
            )
            return result.acknowledged
        except Exception as e:
            self.logger.error(f"Error saving key information for user {user_id}: {e}")
            return False
