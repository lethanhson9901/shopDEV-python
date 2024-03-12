# In src/utils/security.py

import os
import re
from datetime import datetime, timedelta
from typing import Optional, Union
from dotenv import load_dotenv
from jose import jwt, JWTError
from passlib.context import CryptContext
from src.configs.config import CurrentConfig

# Load environment variables from .env file
load_dotenv()

# Pre-compile the regular expression pattern for password complexity
# to improve performance.
PASSWORD_PATTERN = re.compile(
    r'^(?=.*[A-Za-z])(?=.*\d)(?=.*[@$!%*#?&])[A-Za-z\d@$!%*#?&]{8,}$'
)

# Initialize the password context for hashing and verifying passwords
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def is_password_complex(password: str) -> bool:
    """
    Validates the complexity of a password against a predefined pattern.
    
    Parameters:
    - password (str): The password to validate.
    
    Returns:
    - bool: True if the password meets the complexity requirements, 
            False otherwise.
    """
    return bool(PASSWORD_PATTERN.match(password))


async def hash_password(password: str) -> str:
    """
    Asynchronously hashes a password using bcrypt.
    
    Parameters:
    - password (str): The password to hash.
    
    Returns:
    - str: The hashed password.
    """
    return pwd_context.hash(password)


async def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Asynchronously verifies a plain password against its hashed version.
    
    Parameters:
    - plain_password (str): The plain text password to verify.
    - hashed_password (str): The hashed password to compare against.
    
    Returns:
    - bool: True if the verification is successful, False otherwise.
    """
    return pwd_context.verify(plain_password, hashed_password)


def get_jwt_secret_key() -> str:
    """
    Retrieves the appropriate secret key for JWT operations based on
    the configured algorithm. Adjusted to ensure RSA keys are returned
    in PEM format as a string.
    
    Returns:
    - str: The secret key or private key for JWT encoding.
    """
    if CurrentConfig.ALGORITHM in ["RS256", "ES256"]:
        # Assuming you adjust CurrentConfig.load_private_key() to return
        # the PEM-encoded string directly
        return CurrentConfig.load_private_key()
    else:
        return CurrentConfig.PRIVATE_KEY

def get_jwt_public_key() -> str:
    """
    Retrieves the appropriate secret key for JWT operations based on
    the configured algorithm. Adjusted to ensure RSA keys are returned
    in PEM format as a string.
    
    Returns:
    - str: The secret key or public key for JWT encoding.
    """
    if CurrentConfig.ALGORITHM in ["RS256", "ES256"]:
        # Assuming you adjust CurrentConfig.load_public_key() to return
        # the PEM-encoded string directly
        return CurrentConfig.load_public_key()
    else:
        return CurrentConfig.PUBLIC_KEY

def create_token(data: dict, 
                 expires_delta: Optional[timedelta] = None,
                 is_refresh_token: bool = False) -> str:
    """
    Creates a JWT token with optional expiration and refresh capabilities.
    
    Parameters:
    - data (dict): The payload data for the token.
    - expires_delta (Optional[timedelta]): Optional expiration delta from now.
    - is_refresh_token (bool): Indicates if the token is a refresh token.
    
    Returns:
    - str: The encoded JWT token.
    """
    expire_minutes = (CurrentConfig.REFRESH_TOKEN_EXPIRE_MINUTES
                      if is_refresh_token
                      else CurrentConfig.ACCESS_TOKEN_EXPIRE_MINUTES)
    expire = datetime.utcnow() + (expires_delta or 
                                   timedelta(minutes=expire_minutes))
    
    token_type = "refresh" if is_refresh_token else "access"
    
    to_encode = data.copy()
    to_encode.update({
        "exp": expire,
        "type": token_type  # Add token type to the payload
    })
    
    return jwt.encode(to_encode, get_jwt_secret_key(),
                      algorithm=CurrentConfig.ALGORITHM)


async def decode_token(token: str) -> dict:
    """
    Decodes a JWT token (either access or refresh) and validates its integrity,
    supporting RS256, ES256, and HS256 algorithms.

    Parameters:
    - token (str): The JWT token to decode and validate.

    Returns:
    - dict: The payload of the decoded JWT token if valid.

    Raises:
    - JWTError: If the token is invalid or expired.
    """
    try:
        # Determine the appropriate key based on the algorithm
        if CurrentConfig.ALGORITHM in ["RS256", "ES256"]:
            key = get_jwt_public_key()  # Use the public key for RSA and ECDSA
        elif CurrentConfig.ALGORITHM == "HS256":
            key = get_jwt_secret_key()  # Use the secret key for HMAC
        else:
            raise ValueError(f"Unsupported JWT algorithm: {CurrentConfig.ALGORITHM}")

        # Decode the token with the selected key
        payload = jwt.decode(token, key, algorithms=[CurrentConfig.ALGORITHM])
        return payload
    except JWTError as e:
        raise JWTError(f"Invalid or expired token: {e}")
    except ValueError as e:
        raise ValueError(str(e))