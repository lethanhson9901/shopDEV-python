# path/filename: src/models/user_models.py
from pydantic import BaseModel, Field, EmailStr, validator
from enum import Enum
from typing import Optional
import re
from src.utils.role_permissions import Role
from datetime import date

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
    first_name: str = Field(
        ...,
        example="John",
        description="The user's first name."
    )
    last_name: str = Field(
        ...,
        example="Doe",
        description="The user's last name."
    )
    date_of_birth: Optional[date] = Field(
        None,
        example="1990-01-01",
        description="The user's date of birth."
    )
    mobile_phone: Optional[str] = Field(
        None,
        example="+1234567890",
        description="The mobile phone number of the user."
    )
    address: Optional[str] = Field(
        None,
        example="1234 Main St, Anytown, Country",
        description="The physical address of the user."
    )

class SignupRequestModel(BaseModel):
    email: EmailStr = Field(
        ...,
        example="user@gmail.com",
        description="The unique email address of the user."
    )
    password: str = Field(
        ...,
        min_length=8,
        max_length=128,
        description="User password with at least 8 characters, including a number and a special character.",
        example="SecurePassword123!"
    )
    first_name: str = Field(
        ...,
        example="John",
        description="The user's first name."
    )
    last_name: str = Field(
        ...,
        example="Doe",
        description="The user's last name."
    )
    mobile_phone: str = Field(
        ...,
        example="+1234567890",
        description="The mobile phone number of the user."
    )
    address: str = Field(
        ...,
        example="1234 Main St, Anytown, Country",
        description="The physical address of the user."
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

class LoginRequestModel(BaseModel):
    email: EmailStr = Field(
        ...,
        description="The user's email address for login."
    )
    password: str = Field(
        ...,
        description="The user's password for login."
    )

class LoginResponseModel(BaseModel):
    access_token: str
    token_type: str
    refresh_token: str

class SignupResponseModel(BaseModel):
    message: str
    user_id: str
    role: UserRole
