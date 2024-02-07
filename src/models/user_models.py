# src/models/user_models.py
from pydantic import BaseModel, Field, EmailStr, validator, ValidationError
import re

class BaseUserModel(BaseModel):
    email: EmailStr = Field(
        ...,
        example="user@example.com",
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

    @validator('password')
    def password_complexity_check(cls, v, values, **kwargs):
        pattern = r'^(?=.*[A-Za-z])(?=.*\d)(?=.*[@$!%*#?&])[A-Za-z\d@$!%*#?&]{8,}$'
        if not re.match(pattern, v):
            raise ValueError('Password must contain at least one letter, one number, and one special character')
        if 'email' in values and values['email'].split('@')[0] in v:
            raise ValueError('Password should not contain your email name')
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
    refresh_token: str  # Added refresh token field


class SignupResponseModel(BaseModel):
    message: str
    user: dict
    # Define other fields as needed, ensuring sensitive information like passwords are excluded