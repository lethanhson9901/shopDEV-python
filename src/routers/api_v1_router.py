# src/routers/api_v1_router.py

from fastapi import APIRouter
from src.routers.access.users_router import users_router

api_v1_router = APIRouter()

api_v1_router.include_router(users_router, prefix="/users")
