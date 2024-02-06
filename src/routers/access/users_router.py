# src/routers/access/user_router.py

from fastapi import APIRouter, status, Response
from src.controllers.access_controller import signup_user, login_user
from src.models.user_models import SignupRequestModel, LoginRequestModel
from src.schemas.signup_schema import SignupResponseModel 
from src.schemas.login_schema import LoginResponseModel

users_router = APIRouter()

@users_router.post("/signup", response_model=SignupResponseModel, status_code=status.HTTP_201_CREATED)
async def signup(signup_request: SignupRequestModel):
    return await signup_user(signup_request)

@users_router.post("/login", response_model=LoginResponseModel)
async def login(login_request: LoginRequestModel, response: Response):
    result = await login_user(login_request)
    return result
