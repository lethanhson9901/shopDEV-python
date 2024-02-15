# src/services/user_service.py

from src.models.user_models import SignupRequestModel
from src.utils.security import hash_password, verify_password, create_token, is_password_complex
from src.utils.email_reset import send_reset_email
from src.dbs.db_manager import DBManager
from bson import ObjectId
from datetime import datetime
import re
from src.core.success_response_handler import SuccessResponseHandler
from src.core.user_error_response_handler import UserErrorResponseHandler

db_manager = DBManager()

async def register_user(signup_request: SignupRequestModel) -> dict:
    if await db_manager.find_user_by_email(signup_request.email):
        UserErrorResponseHandler.email_already_registered()
    
    hashed_password = await hash_password(signup_request.password)
    current_time = datetime.now()
    user_data = signup_request.dict(exclude={"password"})
    user_data.update({"password": hashed_password, "created_at": current_time, "updated_at": current_time})
    
    try:
        new_user_id = await db_manager.insert_user(user_data)
    except Exception:
        UserErrorResponseHandler.password_update_error()
    
    user_response_data = {k: str(v) if isinstance(v, ObjectId) else v.isoformat() if isinstance(v, datetime) else v for k, v in user_data.items() if k not in ["password"]}
    user_response_data["user_id"] = str(new_user_id)

    # Use SuccessResponseHandler for user registration success response
    return SuccessResponseHandler.user_registered(user_response_data)

async def authenticate_user(email: str, password: str) -> dict:
    user = await db_manager.find_user_by_email(email)
    if not user or not await verify_password(password, user['password']):
        UserErrorResponseHandler.incorrect_email_or_password()

    access_token = create_token(data={"sub": user["email"]}, is_refresh_token=False)
    refresh_token = create_token(data={"sub": user["email"]}, is_refresh_token=True)
    user_role = user.get('role', 'Unknown')

    # Use SuccessResponseHandler for user authentication success response
    return SuccessResponseHandler.user_authenticated(access_token, refresh_token, user_role)

async def update_password(email: str, current_password: str, new_password: str) -> dict:
    user = await db_manager.find_user_by_email(email)
    if not user or not await verify_password(current_password, user['password']):
        UserErrorResponseHandler.incorrect_email_or_password()
    
    if not is_password_complex(new_password):
        UserErrorResponseHandler.bad_request(detail="New password does not meet complexity requirements")
    
    hashed_new_password = await hash_password(new_password)
    
    try:
        await db_manager.update_user_password(email, hashed_new_password)
    except Exception:
        UserErrorResponseHandler.password_update_error()

    # Use SuccessResponseHandler for password update success response
    return SuccessResponseHandler.password_updated()

async def initiate_password_reset(email: str) -> dict:
    user = await db_manager.find_user_by_email(email)
    if not user:
        UserErrorResponseHandler.user_not_found()
    
    reset_token = create_token(data={"user_id": str(user['_id'])}, is_refresh_token=False, expiry_period=3600)
    
    await db_manager.store_reset_token(email, reset_token)
    
    try:
        send_reset_email(user_email=email, token=reset_token)
    except Exception:
        UserErrorResponseHandler.password_reset_failed()

    # Assuming a success response method for password reset initiation is needed
    # For example, using a generic success response here
    return SuccessResponseHandler.general_success(data={}, message="Password reset email sent successfully")
