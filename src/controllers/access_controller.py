# src/controllers/access_controller.py
from fastapi import HTTPException
from fastapi.responses import JSONResponse
from src.models.user_models import (
    SignupRequestModel, LogoutRequestModel, 
    RenewAccessTokenResponseModel, RefreshTokenRequestModel, 
    ChangePasswordRequestModel
)
from src.services.user_service import UserService

class AccessController:
    def __init__(self) -> None:
        self.user_service = UserService()

    async def signup_user(self, signup_request: SignupRequestModel) -> JSONResponse:
        """
        Registers a new user with the given signup request data.

        Args:
            signup_request: The user's signup request details.

        Returns:
            A JSONResponse containing the signup result.
        """
        result = await self.user_service.register_user(signup_request)
        if "error" in result:
            raise HTTPException(status_code=result["status"], detail=result["error"])
        return JSONResponse(status_code=201, content=result)

    async def login_user(self, email: str, password: str) -> JSONResponse:
        """
        Authenticates a user and generates JWT access and refresh tokens.

        Args:
            email: The user's email.
            password: The user's password.

        Returns:
            A JSONResponse containing the authentication result.
        """
        result = await self.user_service.login(email, password)
        
        if "error" in result:
            raise HTTPException(status_code=result["status"], detail=result["error"])
        return JSONResponse(status_code=200, content=result.get('data'))

    async def change_password(self, change_pwd_request: ChangePasswordRequestModel) -> JSONResponse:
        """
        Updates the user's password.

        Args:
            change_pwd_request: Details for changing the user's password.

        Returns:
            A JSONResponse indicating the outcome of the password change.
        """
        try:
            result = await self.user_service.update_password(
                email=change_pwd_request.user_email,
                current_password=change_pwd_request.current_password,
                new_password=change_pwd_request.new_password
            )
            return JSONResponse(status_code=200, content=result)
        except HTTPException as e:
            raise e
        except Exception as e:
            raise HTTPException(status_code=500, detail="An unexpected error occurred.")

    async def refresh_access_token_endpoint(self, refresh_request: RefreshTokenRequestModel) -> RenewAccessTokenResponseModel:
        """
        Refreshes an access token using a valid refresh token.

        Args:
            refresh_request: The refresh token request details.

        Returns:
            A new access token.
        """
        try:
            result = await self.user_service.renew_access_token(refresh_request.refresh_token)
            if "error" in result:
                raise HTTPException(status_code=result["status"], detail=result["error"])
            return result
        except HTTPException as e:
            raise e
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {e}")

    async def logout_user(self, logout_request: LogoutRequestModel) -> JSONResponse:
        """
        Logs out a user by invalidating their current refresh token.

        Args:
            logout_request: The logout request details.

        Returns:
            A JSONResponse indicating the outcome of the logout operation.
        """
        try:
            result = await self.user_service.logout(logout_request.user_id, logout_request.refresh_token)
            if "error" in result:
                raise HTTPException(status_code=result["status"], detail=result["error"])
            return JSONResponse(status_code=200, content={"message": "Successfully logged out"})
        except HTTPException as e:
            raise e
        except Exception as e:
            raise HTTPException(status_code=500, detail="An unexpected error occurred.")
