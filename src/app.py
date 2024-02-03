# src/app.py

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import time
import logging
from brotli_asgi import BrotliMiddleware
from src.dbs.init_mongodb import Database, start_monitoring
from src.utils.status_codes import STATUS_TEXTS
import asyncio
app = FastAPI()

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

# Init middlewares
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(BrotliMiddleware)

@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    
    try:
        response = await call_next(request)
    except Exception as e:
        logger.error("Request processing error: %s", str(e))
        raise  # Re-raise the exception to handle it according to the FastAPI's error handling mechanism
    
    process_time = time.time() - start_time
    client_host = request.client.host if request.client else "client host unknown"
    request_line = f'"{request.method} {request.url.path} HTTP/{request.scope["http_version"]}" {request.url}'
    status_text = STATUS_TEXTS.get(response.status_code, "Status Text Unknown")
    
    logger.info(f"{client_host} - {request_line} {response.status_code} {status_text} {process_time:.6f}")
    
    return response

db_instance = Database()  # Instantiate the Database outside event handlers for clarity

@app.on_event("startup")
async def startup_db_client():
    await db_instance.connect()
    # Start system resource monitoring in the background
    asyncio.create_task(start_monitoring())

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
