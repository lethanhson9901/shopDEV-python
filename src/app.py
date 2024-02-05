# src/app.py
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from brotli_asgi import BrotliMiddleware
import asyncio
from src.dbs.init_mongodb import Database, start_monitoring
from src.helpers.log_config import setup_logger, log_requests, scheduled_cleanup
from src.routers.welcome_router import router as welcome_router

app = FastAPI(title='Python-Dev API', description='A sample FastAPI application.', version='1.0.0')

logger = setup_logger()

# Declare db_instance at the module level to ensure it's accessible in the shutdown event
db_instance = Database()

def configure_middlewares(application: FastAPI):
    """Configure application middlewares."""
    application.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"]
    )
    application.add_middleware(BrotliMiddleware)

def configure_logging_middleware(application: FastAPI):
    """Add logging middleware to the application."""
    application.middleware("http")(log_requests)

def include_routers(application: FastAPI):
    """Include application routers."""
    application.include_router(welcome_router)

@app.on_event("startup")
async def startup_event():
    """Application startup: connect to the database, start background tasks."""
    await db_instance.connect()
    asyncio.create_task(start_monitoring())
    logs_dir = 'logs'  # Ensure this directory exists or is created
    asyncio.create_task(scheduled_cleanup(logs_dir, 30))  # Cleanup interval as needed

@app.on_event("shutdown")
async def shutdown_event():
    """Application shutdown: disconnect from the database."""
    await db_instance.disconnect()

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Handle global exceptions."""
    logger.error(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={"message": "An unexpected error occurred."}
    )

# Apply configuration functions
configure_middlewares(app)
configure_logging_middleware(app)
include_routers(app)
