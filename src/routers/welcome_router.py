# src/routers/index.py

from fastapi import APIRouter, Request
from src.helpers.log_config import setup_logger

logger = setup_logger()
router = APIRouter()

@router.get("/")
async def root(request: Request):
    # Minimal response data for logging
    message = "Welcome to my new world"
    # Return the response data directly without logging it
    return {"message": message}
