# src/services/user_service.py

from src.models.user_models import SignupRequestModel
from src.dbs.key_db_manager import KeyDBManager
from src.utils.security import (
    JWTError, hash_password, verify_password, create_token, decode_token, is_password_complex, get_jwt_public_key, get_jwt_secret_key
)
from src.utils.email_reset import send_reset_email
from src.dbs.user_db_manager import UserDBManager
from bson import ObjectId
from datetime import datetime
from typing import Dict
from src.core.success_response_handler import SuccessResponseHandler
from src.core.user_error_response_handler import UserErrorResponseHandler

user_db_manager = UserDBManager()
key_db_manager = KeyDBManager()

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

async def login(email: str, password: str) -> Dict[str, str]:
    """
    Login a user based on the provided email and password.

    Asynchronously verifies user credentials against the database, generates access
    and refresh tokens, and saves key information. If authentication is successful,
    returns the tokens and user role.

    Parameters:
    - email (str): The user's email address.
    - password (str): The user's password.

    Returns:
    - dict: A dictionary containing 'access_token', 'refresh_token', and 'user_role'.

    Raises:
    - UserErrorResponse: If the email or password is incorrect.
    """
    
    # Attempt to find the user by email
    user = await user_db_manager.find_user_by_email(email)
    if not user or not await verify_password(password, user['password']):
        # Handle incorrect email or password error
        UserErrorResponseHandler.incorrect_email_or_password()

    # Generate tokens
    access_token = create_token(data={"sub": str(user["_id"])}, is_refresh_token=False)
    refresh_token = create_token(data={"sub": str(user["_id"])}, is_refresh_token=True)

    
    # Load key configuration
    public_key = get_jwt_public_key()
    private_key = get_jwt_secret_key()

    # Save key information asynchronously
    await key_db_manager.save_key_information(
        user_id=str(user["_id"]),
        refresh_token=refresh_token,
        public_key=public_key,  # Assumes public_key is correctly loaded
        private_key=private_key  # Assumes private_key is correctly loaded
    )
    
    # Retrieve or default user role
    user_role = user.get('role', 'Unknown')

    # Return successful authentication response
    return SuccessResponseHandler.user_authenticated(
        access_token=access_token,
        refresh_token=refresh_token,
        user_role=user_role
    )

async def renew_access_token(refresh_token: str) -> Dict[str, str]:
    """
    Validates a refresh token and returns a new access token if valid.

    Parameters:
    - refresh_token (str): The refresh token to validate.

    Returns:
    - dict: A dictionary containing the new 'access_token' and 'user_role' if the refresh token is valid.

    Raises:
    - UserErrorResponse: If the refresh token is invalid or expired.
    """
    try:
        payload = await decode_token(refresh_token)
        user_id = payload.get("sub")

        if not user_id:
            return UserErrorResponseHandler.invalid_token()

        user = await user_db_manager.find_user_by_id(user_id)
        if not user:
            return UserErrorResponseHandler.user_not_found()

        key_info = await key_db_manager.find_key_information(user_id)

        # New condition: Check if key_info does not exist
        if not key_info:
            return UserErrorResponseHandler.invalid_token()

        # Check if the refresh token has already been used
        if refresh_token in key_info.get("refresh_tokens_used", []):
            # Security response: delete the token from the list and return an error
            await key_db_manager.delete_refresh_token(user_id, refresh_token)
            return UserErrorResponseHandler.suspicious_activity_detected()
        
        # Add the current refresh token to the list of used tokens before issuing a new one
        token_add_success = await key_db_manager.add_refresh_token_to_list(user_id, refresh_token)
        if not token_add_success:
            # Handle the failure to add the refresh token to the list appropriately
            return UserErrorResponseHandler.operation_failed("Failed to record the refresh token.")

        # Proceed with creating a new access token
        new_access_token = create_token(data={"sub": user_id}, is_refresh_token=False)
        new_refresh_token = create_token(data={"sub": str(user["_id"])}, is_refresh_token=True)

        user_role = user.get('role', 'Unknown')

        # Return the newly generated access token and user role
        return SuccessResponseHandler.renewed_access_token(access_token=new_access_token, 
                                                           refresh_token = new_refresh_token, 
                                                           role=user_role)

    except JWTError as e:
        return UserErrorResponseHandler.invalid_token(message=str(e))


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


async def logout(user_id: str, refresh_token: str) -> dict:
    """
    Logs out a user by invalidating their refresh token.

    Parameters:
    - user_id: The user's unique identifier.
    - refresh_token: The refresh token to invalidate.

    Returns:
    - A success response indicating the user has been logged out.
    """
    # Validate user_id and refresh_token
    key_info = await key_db_manager.find_key_information(user_id)
    if not key_info:
        return UserErrorResponseHandler.invalid_token()

    # Delete the refresh token
    await key_db_manager.delete_refresh_token(user_id, refresh_token)

    return SuccessResponseHandler.general_success(
        data={}, message="Successfully logged out"
    )