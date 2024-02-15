# src/routers/access/user_router.py

from fastapi import APIRouter, status, Response
from src.controllers.access_controller import signup_user, login_user
from src.models.user_models import SignupRequestModel, LoginRequestModel, SignupResponseModel, LoginResponseModel


users_router = APIRouter()

@users_router.post("/signup", response_model=SignupResponseModel, status_code=status.HTTP_201_CREATED)
async def signup(signup_request: SignupRequestModel):
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
    """
    return await signup_user(signup_request)

@users_router.post("/login", response_model=LoginResponseModel)
async def login(login_request: LoginRequestModel, response: Response):
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
    return await login_user(login_request)

