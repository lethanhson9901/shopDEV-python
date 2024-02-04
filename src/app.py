# src/app.py

from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import time
from brotli_asgi import BrotliMiddleware
from src.dbs.init_mongodb import Database, start_monitoring
from src.utils.status_codes import STATUS_TEXTS
import asyncio
from src.helpers.log_config import setup_logger, log_requests, scheduled_cleanup

logger = setup_logger()


app = FastAPI()

# Initialize middlewares
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])
app.add_middleware(BrotliMiddleware)

# Request logging middleware
app.middleware("http")(log_requests)


db_instance = Database()  # Instantiate the Database outside event handlers for clarity

@app.on_event("startup")
async def startup_db_client():
    # Connect to the database
    await db_instance.connect()
    
    # Start system resource monitoring in the background
    asyncio.create_task(start_monitoring())
    
    # Specify the directory where your logs are stored and start the scheduled log cleanup task
    logs_dir = 'logs'  # Adjust this path if necessary
    asyncio.create_task(scheduled_cleanup(logs_dir, 30))  # Schedule log cleanup task

@app.get("/items/{item_id}")
async def read_item(item_id: str):
    db = await db_instance.get_db()
    collection = db['tson']  # Replace with your actual collection name
    item = await collection.find_one({"item_id": item_id})
    if item:
        return item
    return JSONResponse(status_code=404, content={"message": "Item not found"})

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception: {exc}")  # Log unhandled exceptions for debugging
    return JSONResponse(
        status_code=500,
        content={"message": "An unexpected error occurred."},
    )
