# src/auth/authentication_middleware.py

from fastapi import Header, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from src.utils.security import decode_token
from src.dbs.key_db_manager import KeyDBManager
from src.core.auth_error_response_handler import AuthErrorResponseHandler  # Import the AuthErrorResponseHandler

class JWTAuthentication:
    oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/users/login")

    @staticmethod
    async def get_key_db_manager():
        """Dependency injection for KeyDBManager."""
        return KeyDBManager()

    @classmethod
    async def authenticate_token(cls, token: str = Depends(oauth2_scheme)):
        """
        Middleware to authenticate JWT tokens in FastAPI.
        
        Args:
            token (str): The JWT token extracted by FastAPI's OAuth2PasswordBearer.
        """
        print(f"Received token: {token}")  # Added for debugging
        if token is None:
            AuthErrorResponseHandler.missing_authorization_header()
        try:
            payload = await decode_token(token)
        except JWTError:
            AuthErrorResponseHandler.credentials_validation_failed()

        user_id = payload.get("sub")
        if not user_id:
            AuthErrorResponseHandler.user_id_extraction_failed()

        key_db_manager = await cls.get_key_db_manager()
        key_info = await key_db_manager.find_key_information(user_id)
        if key_info is None:
            AuthErrorResponseHandler.key_information_not_found()

        return {"user_id": user_id, "refresh_token": key_info.get('refresh_token')}

    # You can include any additional methods here as needed, following the
    # structure and functionality from the provided AuthenticationService example.

