# path/filename: src/models/user_models.py
from pydantic import BaseModel, Field, EmailStr, validator,  ValidationError
from enum import Enum
from typing import Optional
import re
from datetime import datetime
from src.utils.role_permissions import Permission, Role
from src.utils.security import PASSWORD_PATTERN

class UserRole(str, Enum):
    SHOP_OWNER = "shop_owner"
    CUSTOMER = "customer"
    ADMIN = "admin"
    SHOP_MANAGER = "shop_manager"  # New role
    
# Map UserRole to Role with permissions
ROLE_PERMISSION_MAP = {
    UserRole.SHOP_OWNER: Role.SHOP_OWNER,
    UserRole.CUSTOMER: Role.CUSTOMER,
    UserRole.ADMIN: Role.ADMIN,
    UserRole.SHOP_MANAGER: Role.SHOP_MANAGER,  # Mapping the new role
}

class BaseUserModel(BaseModel):
    email: EmailStr = Field(
        ...,
        example="user@gmail.com",
        description="The unique email address of the user."
    )
    created_at: Optional[datetime] = Field(default=None, description="Timestamp when the user account was created.")
    updated_at: Optional[datetime] = Field(default=None, description="Timestamp of the last update to the user account.")
    
    # Add a root validator to automatically set created_at and updated_at
    @validator('created_at', 'updated_at', pre=True, always=True)
    def default_datetime(cls, v, values, field):
        if field.name == 'created_at' and not v:
            return datetime.now()
        if field.name == 'updated_at':
            return datetime.now()
        return v

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
        pattern = PASSWORD_PATTERN
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

class ChangePasswordRequestModel(BaseModel):
    user_email: EmailStr = Field(
        ...,
        description="The email address of the user requesting the password change."
    )
    current_password: str = Field(
        ...,
        min_length=8,
        max_length=128,
        description="The current password of the user.",
        example="CurrentPassword123!"
    )
    new_password: str = Field(
        ...,
        min_length=8,
        max_length=128,
        description="The new password for the user. Must meet the complexity requirements.",
        example="NewSecurePassword123!"
    )
    
    @validator('new_password')
    def new_password_complexity_check(cls, v):
        pattern = PASSWORD_PATTERN
        if not re.match(pattern, v):
            raise ValueError('New password must contain at least one letter, one number, and one special character')
        return v

class ChangePasswordResponseModel(BaseModel):
    message: str
    
class PasswordResetRequestModel(BaseModel):
    email: EmailStr = Field(
        ...,
        example="user@example.com",
        description="The email address of the user requesting a password reset."
    )

class PasswordResetModel(BaseModel):
    reset_token: str = Field(
        ...,
        description="The password reset token provided to the user.",
        example="reset_token_12345"
    )
    new_password: str = Field(
        ...,
        min_length=8,
        max_length=128,
        description="The new password for the user. Must meet the complexity requirements.",
        example="ResetNewPassword123!"
    )
    
    @validator('new_password')
    def new_password_complexity_check(cls, v):
        pattern = PASSWORD_PATTERN
        if not re.match(pattern, v):
            raise ValueError('New password must contain at least one letter, one number, and one special character')
        return v

class RefreshTokenRequestModel(BaseModel):
    refresh_token: str = Field(
        ...,
        description="The refresh token to be renewed."
    )

class RenewAccessTokenResponseModel(BaseModel):
    access_token: str = Field(
        ...,
        description="The newly generated JWT access token."
    )
    token_type: str = Field(
        default="bearer",
        description="The type of the token issued."
    )
    role: UserRole = Field(
        ...,
        description="The role of the user associated with the access token."
    )
