# src/services/user_service.py

from src.models.user_models import SignupRequestModel
from src.utils.security import (
    hash_password, verify_password, create_token, is_password_complex
)
from src.utils.email_reset import send_reset_email
from src.dbs.user_db_manager import UserDBManager
from bson import ObjectId
from datetime import datetime
import re
from src.core.success_response_handler import SuccessResponseHandler
from src.core.user_error_response_handler import UserErrorResponseHandler

user_db_manager = UserDBManager()

async def register_user(signup_request: SignupRequestModel) -> dict:
    """
    Registers a new user with the provided signup request data.

    Parameters:
    - signup_request: An instance of SignupRequestModel containing the user's signup details.

    Returns:
    - A dictionary containing the registered user's response data.

    Raises:
    - Raises an error response if the email is already registered.
    """
    if await user_db_manager.find_user_by_email(signup_request.email):
        UserErrorResponseHandler.email_already_registered()

    hashed_password = await hash_password(signup_request.password)
    current_time = datetime.now()
    user_data = signup_request.dict(exclude={"password"})
    user_data.update({
        "password": hashed_password,
        "created_at": current_time,
        "updated_at": current_time
    })

    try:
        new_user_id = await user_db_manager.insert_user(user_data)
    except Exception:
        UserErrorResponseHandler.password_update_error()

    user_response_data = {
        k: str(v) if isinstance(v, ObjectId) else v.isoformat() if isinstance(v, datetime) else v
        for k, v in user_data.items() if k not in ["password"]
    }
    user_response_data["user_id"] = str(new_user_id.inserted_id)

    return SuccessResponseHandler.user_registered(user_response_data)

async def authenticate_user(email: str, password: str) -> dict:
    """
    Authenticates a user with the given email and password.

    Parameters:
    - email: The user's email address.
    - password: The user's password.

    Returns:
    - A dictionary containing the access and refresh tokens along with the user's role.

    Raises:
    - Raises an error response if the email or password is incorrect.
    """
    user = await user_db_manager.find_user_by_email(email)
    if not user or not await verify_password(password, user['password']):
        UserErrorResponseHandler.incorrect_email_or_password()

    access_token = create_token(data={"sub": user["email"]}, is_refresh_token=False)
    refresh_token = create_token(data={"sub": user["email"]}, is_refresh_token=True)
    user_role = user.get('role', 'Unknown')

    return SuccessResponseHandler.user_authenticated(
        access_token, refresh_token, user_role
    )

async def update_password(email: str, current_password: str, new_password: str) -> dict:
    """
    Updates the password for a user identified by email.

    Parameters:
    - email: The user's email address.
    - current_password: The current password of the user.
    - new_password: The new password to set for the user.

    Returns:
    - A success response indicating the password has been updated.

    Raises:
    - Raises an error response if the current password is incorrect or the new password does not meet complexity requirements.
    """
    user = await user_db_manager.find_user_by_email(email)
    if not user or not await verify_password(current_password, user['password']):
        UserErrorResponseHandler.incorrect_email_or_password()

    if not is_password_complex(new_password):
        UserErrorResponseHandler.bad_request(detail="New password does not meet complexity requirements")

    hashed_new_password = await hash_password(new_password)

    try:
        await user_db_manager.update_user_password(email, hashed_new_password)
    except Exception:
        UserErrorResponseHandler.password_update_error()

    return SuccessResponseHandler.password_updated()

async def initiate_password_reset(email: str) -> dict:
    """
    Initiates a password reset process for a user identified by email.

    Parameters:
    - email: The user's email address for which the password reset is initiated.

    Returns:
    - A success response indicating that a password reset email has been sent.

    Raises:
    - Raises an error response if the user cannot be found or if sending the reset email fails.
    """
    user = await user_db_manager.find_user_by_email(email)
    if not user:
        UserErrorResponseHandler.user_not_found()

    reset_token = create_token(data={"user_id": str(user['_id'])}, is_refresh_token=False, expiry_period=3600)

    # Assuming store_reset_token is a method implemented elsewhere to store the reset token
    await user_db_manager.store_reset_token(email, reset_token)

    try:
        send_reset_email(user_email=email, token=reset_token)
    except Exception:
        UserErrorResponseHandler.password_reset_failed()

    return SuccessResponseHandler.general_success(
        data={}, message="Password reset email sent successfully"
    )
