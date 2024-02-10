# src/services/user_service.py

from src.models.user_models import SignupRequestModel
from src.utils.security import hash_password, create_token
from src.utils.security import hash_password, verify_password, create_token
from src.dbs.db_manager import DBManager

db_manager = DBManager()

async def register_user(signup_request: SignupRequestModel) -> dict:
    """Registers a new user with the given signup request data."""
    user = await db_manager.find_user_by_email(signup_request.email)
    if user:
        return {"error": "Email already registered", "status": 409}

    hashed_password = await hash_password(signup_request.password)
    user_data = signup_request.dict(exclude={"password"})
    user_data["password"] = hashed_password
    user_data["role"] = signup_request.role  # Include the role in user_data
    await db_manager.insert_user(user_data)

    user_data["_id"] = str(user_data["_id"])
    del user_data["password"]
    
    return {"message": "User signed up successfully", "user": user_data, "status": 201}


async def authenticate_user(email: str, password: str) -> dict:
    """Authenticates a user and generates JWT access and refresh tokens."""
    user = await db_manager.find_user_by_email(email)
    if not user or not await verify_password(password, user['password']):
        return {"error": "Incorrect email or password", "status": 401}

    access_token = create_token(data={"sub": user["email"]}, is_refresh_token=False)
    refresh_token = create_token(data={"sub": user["email"]}, is_refresh_token=True)

    return {
        "access_token": str(access_token),
        "refresh_token": str(refresh_token),
        "token_type": "bearer",
        "status": 200
    }
