# src/auth/authentication_middleware.py

from fastapi import FastAPI, HTTPException, Depends, Security, status
from fastapi.security import OAuth2PasswordBearer, APIKeyHeader
from jose import jwt, JWTError
from src.utils.security import decode_token
from src.dbs.key_db_manager import KeyDBManager
from src.core.auth_error_response_handler import AuthErrorResponseHandler

class JWTAuthentication:
    oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/users/login")

    @staticmethod
    async def get_key_db_manager():
        """Dependency injection for KeyDBManager."""
        return KeyDBManager()

    @classmethod
    async def authenticate_token(cls, token: str = Depends(oauth2_scheme)):
        """
        Middleware to authenticate JWT tokens and API keys in FastAPI.
        
        Args:
            token (str): The JWT token extracted by FastAPI's OAuth2PasswordBearer.
            api_key (str): The API key extracted from the request header.
        """

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

    # Additional methods as needed, following the structure from AuthenticationService example.


api_key_header = APIKeyHeader(name="x-auth-token", auto_error=False)

def verify_api_key(api_key_header: str = Security(api_key_header)):
    if api_key_header != "secured_api_key":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized API-KEY"
        )