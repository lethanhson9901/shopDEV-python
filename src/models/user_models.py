# path/filename: src/models/user_models.py
from pydantic import BaseModel, Field, EmailStr, validator,  ValidationError
from enum import Enum
from typing import Optional
import re
from datetime import datetime, date
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
    first_name: str = Field(
        ...,
        max_length=50,
        example="John",
        description="The first name of the user."
    )
    last_name: str = Field(
        ...,
        max_length=50,
        example="Doe",
        description="The last name of the user."
    )
    date_of_birth: Optional[str] = Field(
        None,
        example="1990-01-01",
        description="The date of birth of the user. Optional."
    )
    mobile_phone: str = Field(
        ...,
        example="+1234567890",
        description="The mobile phone number of the user."
    )
    address: str = Field(
        ...,
        example="123 Main St, Anytown, Country",
        description="The address of the user."
    )
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

    @validator('mobile_phone')
    def mobile_phone_validator(cls, v):
        pattern = r'^\+\d{10,15}$'
        if not re.match(pattern, v):
            raise ValueError('Mobile phone number must be in the format: + followed by 10 to 15 digits')
        return v
    
    @validator('date_of_birth', pre=True, always=True)
    def validate_date_of_birth(cls, v):
        if v is None:
            return v
        try:
            return str(datetime.strptime(v, "%Y-%m-%d").date())
        except ValueError:
            raise ValueError('Date of birth must be in YYYY-MM-DD format')

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
