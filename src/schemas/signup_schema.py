# src/schemas/signup_schema.py

from pydantic import BaseModel

class SignupResponseModel(BaseModel):
    message: str
    user: dict
    # Define other fields as needed, ensuring sensitive information like passwords are excluded
