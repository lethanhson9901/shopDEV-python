# src/utils/security.py

from passlib.context import CryptContext
from jose import jwt, JWTError
from datetime import datetime, timedelta
from src.configs.config import CurrentConfig
from typing import Optional

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

async def hash_password(password: str) -> str:
    """Hashes a password."""
    return pwd_context.hash(password)

async def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifies a plain password against a hashed one."""
    return pwd_context.verify(plain_password, hashed_password)

def create_token(data: dict, expires_delta: Optional[timedelta] = None, is_refresh_token: bool = False) -> str:
    """Creates a JWT token. Set is_refresh_token=True to generate a refresh token."""
    secret_key = CurrentConfig.SECRET_KEY
    algorithm = CurrentConfig.ALGORITHM
    expire_minutes = CurrentConfig.REFRESH_TOKEN_EXPIRE_MINUTES if is_refresh_token else CurrentConfig.ACCESS_TOKEN_EXPIRE_MINUTES
    expire = datetime.utcnow() + (expires_delta if expires_delta else timedelta(minutes=expire_minutes))
    to_encode = data.copy()
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, secret_key, algorithm)

async def refresh_access_token(refresh_token: str) -> dict:
    """Verifies a refresh token and returns a new access token, handling specific exceptions."""
    try:
        payload = jwt.decode(refresh_token, CurrentConfig.SECRET_KEY, algorithms=[CurrentConfig.ALGORITHM])
        user_id = payload.get("sub")  # Assuming 'sub' contains the user identifier
        if user_id is None:
            raise ValueError("User ID not found in refresh token.")  # Specific exception

        # Optionally, add logic here to verify the refresh token's validity against a database

        new_access_token = create_token(data={"sub": user_id}, is_refresh_token=False)
        return {"access_token": new_access_token, "token_type": "bearer"}
    except JWTError:
        raise ValueError("Invalid refresh token.")  # More specific exception
