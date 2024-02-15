# src/services/user_service.py

from src.models.user_models import SignupRequestModel
from src.utils.security import hash_password, verify_password, create_token, PASSWORD_PATTERN
from src.utils.email_reset import send_reset_email
from src.dbs.db_manager import DBManager
from fastapi import HTTPException
from bson import ObjectId
from datetime import datetime
import re

db_manager = DBManager()


async def register_user(signup_request: SignupRequestModel) -> dict:
    """
    Registers a new user with the provided signup request data, ensuring email uniqueness.
    Handles 'created_at' and 'updated_at' fields automatically.
    """
    # Verify email uniqueness
    if await db_manager.find_user_by_email(signup_request.email):
        raise HTTPException(status_code=409, detail="Email already registered")
    
    # Securely hash the password
    hashed_password = await hash_password(signup_request.password)
    
    # Prepare user data with hashed password and timestamps
    current_time = datetime.now()
    user_data = signup_request.dict(exclude={"password"})
    user_data.update({
        "password": hashed_password,
        "created_at": current_time,
        "updated_at": current_time,
    })
    
    # Insert the new user into the database and handle potential errors
    try:
        new_user_id = await db_manager.insert_user(user_data)
    except Exception as e:
        # Log the error or handle it appropriately
        raise HTTPException(status_code=500, detail="An error occurred during user registration.")
    
    # Prepare response, excluding sensitive data and converting ObjectId to string
    user_response_data = {
        k: str(v) if isinstance(v, ObjectId) else v.isoformat() if isinstance(v, datetime) else v
        for k, v in user_data.items() if k not in ["password"]
    }

    # Ensure the new_user_id is correctly converted to string for JSON serialization
    user_response_data["user_id"] = str(new_user_id)

    return {
        "message": "User signed up successfully",
        "user": user_response_data,
        "status": 201
    }


async def authenticate_user(email: str, password: str) -> dict:
    """Authenticates a user and generates JWT access and refresh tokens, along with the user's role, handling authentication errors."""
    user = await db_manager.find_user_by_email(email)
    if not user or not await verify_password(password, user['password']):
        raise HTTPException(status_code=401, detail="Incorrect email or password")

    access_token = create_token(data={"sub": user["email"]}, is_refresh_token=False)
    refresh_token = create_token(data={"sub": user["email"]}, is_refresh_token=True)

    # Assuming the user's role is stored directly in the user object as 'role'.
    # Adjust the key according to your database schema if needed.
    user_role = user.get('role', 'Unknown')  # Provide a default role or handle as your logic requires

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "role": user_role,  # Include the user's role in the response
        "status": 200
    }


async def update_password(email: str, current_password: str, new_password: str) -> dict:
    """
    Updates the user's password after validating the current password and the complexity of the new password.
    
    Parameters:
    - email (str): The email of the user whose password is to be updated.
    - current_password (str): The current password of the user for verification.
    - new_password (str): The new password to be set for the user.
    
    Returns:
    - dict: A response dictionary indicating the success or failure of the operation.
    """
    # Verify user exists and current password is correct
    user = await db_manager.find_user_by_email(email)
    if not user or not await verify_password(current_password, user['password']):
        raise HTTPException(status_code=401, detail="Incorrect email or current password")
    
    # Validate new password complexity
    if not is_password_complex(new_password):
        raise HTTPException(status_code=400, detail="New password does not meet complexity requirements")
    
    # Hash new password
    hashed_new_password = await hash_password(new_password)
    
    # Update user's password in the database
    try:
        await db_manager.update_user_password(email, hashed_new_password)
        return {"message": "Password updated successfully", "status": 200}
    except Exception as e:
        # Log the error or handle it appropriately
        raise HTTPException(status_code=500, detail="An error occurred during the password update process", error=e)

def is_password_complex(password: str) -> bool:
    """
    Validates the complexity of the password.
    
    Parameters:
    - password (str): The password to be validated.
    
    Returns:
    - bool: True if the password meets complexity requirements, False otherwise.
    """
    pattern = PASSWORD_PATTERN
    return bool(re.match(pattern, password))


async def initiate_password_reset(email: str) -> dict:
    """
    Initiates the password reset process for a user by generating a reset token and sending it via email.
    
    Parameters:
    - email (str): The email of the user requesting a password reset.
    
    Returns:
    - dict: A response dictionary indicating the initiation was successful or an error occurred.
    """
    # Verify user exists
    user = await db_manager.find_user_by_email(email)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Generate a secure token
    reset_token = create_token(data={"user_id": str(user['_id'])}, is_refresh_token=False, expiry_period=3600) # Expires in 1 hour
    
    # Optionally store the token in the database for later verification during password reset
    # This step is implementation-specific and depends on your database schema
    await db_manager.store_reset_token(email, reset_token)
    
    # Send the token to the user's email
    try:
        send_reset_email(user_email=email, token=reset_token)
        return {"message": "Password reset email sent successfully", "status": 200}
    except Exception as e:
        # Handle email sending failure
        raise HTTPException(status_code=500, detail="Failed to send password reset email")
