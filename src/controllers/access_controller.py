# src/controllers/access_controller.py

from fastapi import HTTPException, status, Depends
from datetime import timedelta
from src.models.user_models import SignupRequestModel, LoginRequestModel
from src.utils.security import hash_password, verify_password, create_access_token
from src.dbs.db_manager import DBManager
from src.schemas.login_schema import LoginResponseModel

# Initialize the Database manager instance
db_manager = DBManager()

async def signup_user(signup_request: SignupRequestModel) -> dict:
    user = await db_manager.find_user_by_email(signup_request.email)
    if user:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already registered")
    
    hashed_password = await hash_password(signup_request.password)
    user_data = signup_request.dict(exclude={"password"})
    user_data["password"] = hashed_password
    await db_manager.insert_user(user_data)
    user_data["_id"] = str(user_data["_id"])  # Ensure ObjectId is converted to string
    del user_data["password"]  # Remove password from response for security

    return {"message": "User signed up successfully", "user": user_data}

async def login_user(login_request: LoginRequestModel) -> LoginResponseModel:
    user = await db_manager.find_user_by_email(login_request.email)
    if not user or not await verify_password(login_request.password, user['password']):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token = create_access_token(data={"sub": user["email"]})

    return LoginResponseModel(access_token=str(access_token), token_type="bearer")


# Note: The create_access_token function does not need to be async as it does not perform any IO operations.
