# src/utils/security.py

from passlib.context import CryptContext
from jose import jwt, JWTError
from datetime import datetime, timedelta
from src.configs.config import CurrentConfig
from typing import Optional, Union

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

async def hash_password(password: str) -> str:
    """Asynchronously hashes a password using bcrypt."""
    return pwd_context.hash(password)

async def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Asynchronously verifies a plain password against its hashed counterpart."""
    return pwd_context.verify(plain_password, hashed_password)

def create_token(data: dict, expires_delta: Optional[timedelta] = None, is_refresh_token: bool = False) -> str:
    """Creates a JWT token. Use is_refresh_token=True to generate a refresh token.
    
    Args:
        data (dict): The payload data for the token.
        expires_delta (Optional[timedelta]): The expiration delta from the current time.
        is_refresh_token (bool): Flag to indicate if the token is a refresh token.

    Returns:
        str: The encoded JWT token.
    """
    secret_key = CurrentConfig.SECRET_KEY
    algorithm = CurrentConfig.ALGORITHM
    expire_minutes = CurrentConfig.REFRESH_TOKEN_EXPIRE_MINUTES if is_refresh_token else CurrentConfig.ACCESS_TOKEN_EXPIRE_MINUTES
    expire = datetime.utcnow() + (expires_delta if expires_delta else timedelta(minutes=expire_minutes))
    to_encode = data.copy()
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, secret_key, algorithm)

async def refresh_access_token(refresh_token: str) -> Union[dict, None]:
    """Verifies a refresh token and returns a new access token, handling exceptions for security.
    
    Args:
        refresh_token (str): The refresh token to validate and use for generating a new access token.
    
    Returns:
        Union[dict, None]: A new access token or None if the refresh token is invalid.
    
    Raises:
        ValueError: If the refresh token is invalid or the user ID is not found.
    """
    try:
        payload = jwt.decode(refresh_token, CurrentConfig.SECRET_KEY, algorithms=[CurrentConfig.ALGORITHM])
        user_id = payload.get("sub")  # Assuming 'sub' contains the user identifier.
        if user_id is None:
            raise ValueError("User ID not found in refresh token.")  # Specific exception.

        # Optionally, add logic here to verify the refresh token's validity against a database.
        new_access_token = create_token(data={"sub": user_id}, is_refresh_token=False)
        return {"access_token": new_access_token, "token_type": "bearer"}
    except JWTError as e:
        raise ValueError(f"Invalid refresh token: {e}")  # More specific exception.
