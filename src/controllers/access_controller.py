# src/controllers/access_controller.py

from fastapi import HTTPException, status
from fastapi.responses import JSONResponse
from src.models.user_models import SignupRequestModel, LoginRequestModel
from src.utils.security import hash_password, verify_password, create_token
from src.dbs.db_manager import DBManager
from src.schemas.login_schema import LoginResponseModel

# Initialize the database manager instance
db_manager = DBManager()


async def signup_user(signup_request: SignupRequestModel) -> JSONResponse:
    """Registers a new user with the given signup request data."""
    # Check if the user already exists
    user = await db_manager.find_user_by_email(signup_request.email)
    if user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already registered"
        )

    # Hash the password and prepare user data for insertion
    hashed_password = await hash_password(signup_request.password)
    user_data = signup_request.dict(exclude={"password"})
    user_data["password"] = hashed_password
    result = await db_manager.insert_user(user_data)

    # Convert ObjectId to string and enhance security by removing the password
    user_data["_id"] = str(result.inserted_id)
    del user_data["password"]

    # Return a 201 Created response with user data (excluding sensitive information)
    return JSONResponse(status_code=status.HTTP_201_CREATED, 
                        content={"message": "User signed up successfully", "user": user_data})

async def login_user(login_request: LoginRequestModel) -> LoginResponseModel:
    """Authenticates a user and generates JWT access and refresh tokens."""
    user = await db_manager.find_user_by_email(login_request.email)
    if not user or not await verify_password(login_request.password, user['password']):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"}
        )

    # Generate an access token for the user
    access_token = create_token(data={"sub": user["email"]}, is_refresh_token=False)
    # Generate a refresh token for the user
    refresh_token = create_token(data={"sub": user["email"]}, is_refresh_token=True)

    return LoginResponseModel(access_token=str(access_token), refresh_token=str(refresh_token), token_type="bearer")
