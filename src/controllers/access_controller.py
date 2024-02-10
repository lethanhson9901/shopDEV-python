# src/controllers/access_controller.py

from fastapi import HTTPException
from fastapi.responses import JSONResponse
from src.models.user_models import SignupRequestModel, LoginRequestModel
from src.services.user_service import register_user, authenticate_user

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

