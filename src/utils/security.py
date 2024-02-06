# src/utils/security.py

from passlib.context import CryptContext
from jose import jwt
from datetime import datetime, timedelta
from src.configs.config import CurrentConfig

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

async def hash_password(password: str) -> str:
    return pwd_context.hash(password)

async def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict, expires_delta: timedelta = None):
    SECRET_KEY = CurrentConfig.SECRET_KEY
    ALGORITHM = CurrentConfig.ALGORITHM
    ACCESS_TOKEN_EXPIRE_MINUTES = CurrentConfig.ACCESS_TOKEN_EXPIRE_MINUTES

    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
