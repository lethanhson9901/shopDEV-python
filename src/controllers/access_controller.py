# src/controllers/access_controller.py

from fastapi import HTTPException
from fastapi.responses import JSONResponse
from src.models.user_models import SignupRequestModel, LoginRequestModel, ChangePasswordRequestModel
from src.services.user_service import register_user, authenticate_user, update_password

async def signup_user(signup_request: SignupRequestModel) -> JSONResponse:
    """Registers a new user with the given signup request data."""
    result = await register_user(signup_request)
    if "error" in result:
        raise HTTPException(status_code=result["status"], detail=result["error"])
    return JSONResponse(status_code=result["status"], content=result)

async def login_user(login_request: LoginRequestModel) -> JSONResponse:
    """Authenticates a user and generates JWT access and refresh tokens."""
    result = await authenticate_user(login_request.email, login_request.password)
    if "error" in result:
        raise HTTPException(status_code=result["status"], detail=result["error"])
    return JSONResponse(status_code=result["status"], content=result)

async def change_password(change_pwd_request: ChangePasswordRequestModel) -> JSONResponse:
    """Updates the password for the authenticated user."""

    # Check if the provided current password matches the stored password for the user
    authentication_result = await authenticate_user(change_pwd_request.email, change_pwd_request.current_password)
    if "error" in authentication_result:
        raise HTTPException(status_code=authentication_result["status"], detail=authentication_result["error"])

    # Update the password for the user
    result = await update_password(change_pwd_request.email, change_pwd_request.new_password)
    if "error" in result:
        raise HTTPException(status_code=result["status"], detail=result["error"])

    return JSONResponse(status_code=result["status"], content=result)
