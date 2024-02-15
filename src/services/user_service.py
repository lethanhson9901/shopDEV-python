# src/services/user_service.py

from src.models.user_models import SignupRequestModel
from src.utils.security import hash_password, create_token
from src.utils.security import hash_password, verify_password, create_token
from src.dbs.db_manager import DBManager
from fastapi import HTTPException

db_manager = DBManager()

async def register_user(signup_request: SignupRequestModel) -> dict:
    """Registers a new user with the given signup request data, ensuring email uniqueness."""
    user = await db_manager.find_user_by_email(signup_request.email)
    if user:
        raise HTTPException(status_code=409, detail="Email already registered")

    hashed_password = await hash_password(signup_request.password)
    user_data = signup_request.dict(exclude={"password"})
    user_data["password"] = hashed_password
    # Directly assigning role from SignupRequestModel for clarity
    await db_manager.insert_user(user_data)

    # Exclude sensitive data from the response
    user_data["_id"] = str(user_data["_id"])  # Convert ObjectId to string for JSON serialization
    del user_data["password"]
    
    return {"message": "User signed up successfully", "user": user_data, "status": 201}


async def authenticate_user(email: str, password: str) -> dict:
    """Authenticates a user and generates JWT access and refresh tokens, along with the user's role, handling authentication errors."""
    user = await db_manager.find_user_by_email(email)
    if not user or not await verify_password(password, user['password']):
        raise HTTPException(status_code=401, detail="Incorrect email or password")

    access_token = create_token(data={"sub": user["email"]}, is_refresh_token=False)
    refresh_token = create_token(data={"sub": user["email"]}, is_refresh_token=True)

    # Assuming the user's role is stored directly in the user object as 'role'.
    # Adjust the key according to your database schema if needed.
    user_role = user.get('role', 'Unknown')  # Provide a default role or handle as your logic requires

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "role": user_role,  # Include the user's role in the response
        "status": 200
    }

