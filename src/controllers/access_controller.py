# src/controllers/access_controller.py

from fastapi import HTTPException
from fastapi.responses import JSONResponse
from src.models.user_models import SignupRequestModel, LoginRequestModel, RenewAccessTokenResponseModel, RefreshTokenRequestModel, ChangePasswordRequestModel
from src.services.user_service import register_user, authenticate_user, renew_access_token, update_password

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
    """Updates the user's password."""
    try:
        # Call the update_password function with the provided parameters
        result = await update_password(
            email=change_pwd_request.user_email,
            current_password=change_pwd_request.current_password,
            new_password=change_pwd_request.new_password
        )
        # Return a success response
        return JSONResponse(status_code=result["status"], content=result)
    except HTTPException as e:
        # If an HTTPException is raised, return the error response
        return JSONResponse(status_code=e.status_code, content={"error": e.detail})
    except Exception as e:
        # If any other unexpected exception occurs, return a 500 error response
        return JSONResponse(status_code=500, content={"error": "An unexpected error occurred."})


async def refresh_access_token_endpoint(refresh_request: RefreshTokenRequestModel) -> RenewAccessTokenResponseModel:
    """
    Receives a refresh token and returns a new access token if the refresh token is valid.
    """
    try:
        result = await renew_access_token(refresh_request.refresh_token)
        if "error" in result:
            raise HTTPException(status_code=result["status"], detail=result["error"])
        return result
    except HTTPException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {e}")
