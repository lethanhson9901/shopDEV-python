# src/auth/authentication_middleware.py
from fastapi import Header, Depends
from jose import jwt, JWTError
from src.utils.security import decode_token
from src.dbs.key_db_manager import KeyDBManager
from src.core.auth_error_response_handler import AuthErrorResponseHandler  # Import the AuthErrorResponseHandler

async def get_key_db_manager():
    """Dependency injection for KeyDBManager."""
    return KeyDBManager()

async def jwt_authentication_middleware(
    authorization: str = Header(None),
    key_db_manager: KeyDBManager = Depends(get_key_db_manager)
):
    """
    Middleware to authenticate JWT tokens in FastAPI.

    Args:
        authorization (str): The content of the Authorization header.
        key_db_manager (KeyDBManager): The database manager for key retrieval, injected by FastAPI.
    """
    if authorization is None:
        AuthErrorResponseHandler.missing_authorization_header()

    try:
        scheme, token = authorization.split(' ', 1)
        if scheme.lower() != 'bearer':
            AuthErrorResponseHandler.invalid_authentication_scheme()
        if not token:
            AuthErrorResponseHandler.token_missing()
    except ValueError:
        AuthErrorResponseHandler.invalid_authorization_header_format()

    try:
        payload = await decode_token(token)
    except JWTError:
        AuthErrorResponseHandler.credentials_validation_failed()

    user_id = payload.get("sub")
    if not user_id:
        AuthErrorResponseHandler.user_id_extraction_failed()

    key_info = await key_db_manager.find_key_information(user_id)
    if key_info is None:
        AuthErrorResponseHandler.key_information_not_found()

    return {"user_id": user_id, "refresh_token": key_info.get('refresh_token')}
