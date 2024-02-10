# path/filename: src/models/user_models.py
from pydantic import BaseModel, Field, EmailStr, validator, ValidationError
from enum import Enum
from typing import Optional
import re
from src.utils.role_permissions import Permission, Role

class UserRole(str, Enum):
    SHOP_OWNER = "shop_owner"
    CUSTOMER = "customer"
    ADMIN = "admin"

# Map UserRole to Role with permissions
ROLE_PERMISSION_MAP = {
    UserRole.SHOP_OWNER: Role.SHOP_OWNER,
    UserRole.CUSTOMER: Role.CUSTOMER,
    UserRole.ADMIN: Role.ADMIN,  # Assuming ADMIN has all permissions or specific ones
}

class BaseUserModel(BaseModel):
    email: EmailStr = Field(
        ...,
        example="user@gmail.com",
        description="The unique email address of the user."
    )

class SignupRequestModel(BaseUserModel):
    password: str = Field(
        ...,
        min_length=8,
        max_length=128,
        description="User password with at least 8 characters, including a number and a special character.",
        example="SecurePassword123!"
    )
    role: UserRole = Field(
        ...,
        description="The role of the user.",
        example="customer"
    )

    @validator('password')
    def password_complexity_check(cls, v):
        pattern = r'^(?=.*[A-Za-z])(?=.*\d)(?=.*[@$!%*#?&])[A-Za-z\d@$!%*#?&]{8,}$'
        if not re.match(pattern, v):
            raise ValueError('Password must contain at least one letter, one number, and one special character')
        return v

    @validator('email')
    def email_validator(cls, v, values, **kwargs):
        if '@example.com' in v:
            raise ValueError("Email addresses from 'example.com' are not allowed")
        return v

class LoginRequestModel(BaseUserModel):
    password: str = Field(
        ...,
        example="SecurePassword123!",
        description="The user's password for login."
    )


class LoginResponseModel(BaseModel):
    access_token: str
    token_type: str
    refresh_token: str


class SignupResponseModel(BaseModel):
    message: str
    user_id: str  # Securely reference the user without exposing sensitive data
    role: UserRole  # Include the role to confirm the user's assigned role
