# src/routers/access/user_router.py

from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordRequestForm

from src.controllers.access_controller import AccessController
from src.models.user_models import (
    SignupRequestModel, LogoutRequestModel, LogoutResponseModel,
    RefreshTokenRequestModel, RenewAccessTokenResponseModel,
    SignupResponseModel, LoginResponseModel, ChangePasswordRequestModel,
    ChangePasswordResponseModel
)

users_router = APIRouter(tags=["users"])

# Dependency that creates a new instance of AccessController
def get_access_controller():
    return AccessController()

@users_router.post("/signup", response_model=SignupResponseModel, status_code=status.HTTP_201_CREATED)
async def signup(signup_request: SignupRequestModel, controller: AccessController = Depends(get_access_controller)):
    """
    User Signup

    Allows new users to create an account by providing their personal and contact information, along with their desired role and a secure password. Validates the provided information according to predefined rules and creates a new user record in the system.

    ### Request Body
    - **email**: Unique email address for the user account.
    - **first_name**: User's first name.
    - **last_name**: User's last name.
    - **date_of_birth**: Optional. User's date of birth in "YYYY-MM-DD" format.
    - **mobile_phone**: User's mobile phone number in international format.
    - **address**: Postal address of the user.
    - **password**: Password meeting the complexity requirements.
    - **role**: Desired role of the user within the system (e.g., "customer").

    ### Responses
    - **201 Created**: Successfully created the user account. Returns the user ID and assigned role.
    - **400 Bad Request**: Invalid request data, such as missing required fields or validation failures.
    - **409 Conflict**: The request could not be completed due to a conflict with the current state of the resource (user_id for example). 
    """
    return await controller.signup_user(signup_request)


@users_router.post("/login", response_model=LoginResponseModel)
async def login(form: OAuth2PasswordRequestForm = Depends(), controller: AccessController = Depends(get_access_controller)):
    """
    User Login

    Authenticates a user based on their provided email and password. Upon successful authentication, issues an access token and a refresh token for accessing protected resources.

    ### Request Body
    - **email**: The email address of the user.
    - **password**: The password of the user.

    ### Responses
    - **200 OK**: Authentication successful. Returns access and refresh tokens.
    - **401 Unauthorized**: Authentication failed due to invalid credentials.
    """
    return await controller.login_user(form.username, form.password)


@users_router.post("/change-password", response_model=LoginResponseModel)
async def post_change_password(change_password_request: ChangePasswordRequestModel, controller: AccessController = Depends(get_access_controller)):
    """
    Change Password

    Allows users to change their password by providing their current password and the new password. The new password must meet complexity requirements.

    ### Request Body
    - **user_email**: The email address of the user requesting the password change.
    - **current_password**: The current password of the user.
    - **new_password**: The new password for the user.

    ### Responses
    - **200 OK**: Password changed successfully.
    - **400 Bad Request**: Invalid request data, such as missing required fields or validation failures.
    - **401 Unauthorized**: Authentication failed due to incorrect current password.
    - **500 Internal Server Error**: An unexpected error occurred during the password change process.
    """
    return await controller.change_password(change_password_request)

@users_router.post("/token/refresh", response_model=RenewAccessTokenResponseModel, status_code=status.HTTP_200_OK)
async def refresh_token(refresh_request: RefreshTokenRequestModel, controller: AccessController = Depends(get_access_controller)):
    """
    Refresh Access Token

    Allows users to obtain a new access token using a valid refresh token. Ensures continuous access to protected resources without re-authentication.

    ### Request Body
    - **refresh_token**: The refresh token issued to the user upon login or previous token refresh.

    ### Responses
    - **200 OK**: Successfully refreshed the access token. Returns the new access token.
    - **401 Unauthorized**: Failed to refresh the access token due to an invalid or expired refresh token.
    """
    try:
        return await controller.refresh_access_token_endpoint(refresh_request)
    except HTTPException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)

@users_router.post("/logout", response_model=LogoutResponseModel, status_code=status.HTTP_200_OK)
async def logout(logout_request: LogoutRequestModel, controller: AccessController = Depends(get_access_controller)):
    """
    User Logout

    Invalidates a user's current refresh token, effectively logging them out of the system. Ensures the token cannot be reused for obtaining new access tokens.

    ### Request Body
    - **refresh_token**: The refresh token to be invalidated.

    ### Responses
    - **200 OK**: Successfully logged out.
    - **401 Unauthorized**: Invalid or expired refresh token.
    """
    try:
        return await controller.logout_user(logout_request)
    except HTTPException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)