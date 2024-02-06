# src/helpers/log_config.py

from logging.handlers import RotatingFileHandler
import os
import logging
from typing import Optional
import gzip
import shutil
from datetime import datetime, timedelta
import time
import asyncio
from fastapi import Request, HTTPException, Response
from fastapi.responses import JSONResponse
from starlette.responses import StreamingResponse
from typing import Callable

APP_NAME = 'python-dev'
MAX_RESPONSE_BODY_LOG_LENGTH = 1024

# Global flag to prevent reinitialization of logger
logger_initialized = False
global_logger = None  # Define a global variable for the logger instance


class CustomRotatingFileHandler(RotatingFileHandler):
    """
    A custom file handler for rotating logs at a specified size threshold,
    and incrementing log file names with a counter.
    """
    
    def __init__(
        self, dir_name, app_name, mode='a', max_bytes=0, 
        backup_count=0, encoding: Optional[str] = None, delay: bool = False
    ):
        """
        Initialize the handler.
        """
        self.dir_name = dir_name
        self.app_name = app_name
        super().__init__(self.get_new_logfile_name(), mode, max_bytes, backup_count, encoding, delay)

    def get_new_logfile_name(self):
        """
        Generate a new logfile name based on the current date, existing log count,
        and application name.
        """
        today = datetime.now().strftime("%Y-%m-%d")
        log_files = [filename for filename in os.listdir(self.dir_name)
                     if filename.startswith(self.app_name) and today in filename]
        log_counts = [int(filename.split('-')[-1].split('.')[0]) for filename in log_files
                      if filename.split('-')[-1].split('.')[0].isdigit()]
        next_count = max(log_counts) + 1 if log_counts else 1
        return os.path.join(self.dir_name, f"{self.app_name}-{today}-{next_count}.log")

    def shouldRollover(self, record):
        """
        Determine if rollover should occur based on file size.
        """
        if self.maxBytes == 0:
            return False
        return super().shouldRollover(record)

    def doRollover(self):
        """
        Perform a rollover, as described in __init__().
        """
        self.stream.close()
        if self.backupCount > 0:
            for i in range(self.backupCount - 1, 0, -1):
                source = self.rotation_filename(f"{self.baseFilename}.{i}")
                dest = self.rotation_filename(f"{self.baseFilename}.{i + 1}")
                if os.path.exists(source):
                    if os.path.exists(dest):
                        os.remove(dest)
                    os.rename(source, dest)
            first_backup = self.rotation_filename(f"{self.baseFilename}.1")
            if os.path.exists(first_backup):
                os.remove(first_backup)
            os.rename(self.baseFilename, first_backup)
        if not self.delay:
            self.stream = self._open()
        self.baseFilename = self.get_new_logfile_name()



class GZipRotator:
    """
    GZip rotator for compressing log files upon rotation.
    """

    def __call__(self, source: str, dest: str):
        """
        Compress the log file using gzip.

        Args:
            source (str): The source log file.
            dest (str): The destination file path.
        """
        with open(source, 'rb') as f_in, gzip.open(dest + '.gz', 'wb') as f_out:
            shutil.copyfileobj(f_in, f_out)
        os.remove(source)


def setup_logger() -> logging.Logger:
    """
    Set up and configure the logger with a custom rotating file handler and gzip rotator.

    Returns:
        logging.Logger: The configured logger.
    """
    global global_logger
    if global_logger is None:
        logger = logging.getLogger(__name__)
        logger.setLevel(logging.INFO)
        logs_dir = 'logs'
        if not os.path.exists(logs_dir):
            os.makedirs(logs_dir)

        handler = CustomRotatingFileHandler(app_name=APP_NAME, dir_name=logs_dir, max_bytes=0, backup_count=3, encoding='utf-8')
        handler.rotator = GZipRotator()
        handler.namer = lambda name: name.replace(".log", "") + ".gz"
        formatter = logging.Formatter('%(asctime)s %(levelname)s: %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
        handler.setFormatter(formatter)
        logger.addHandler(handler)

        global_logger = logger  # Store the configured logger in the global variable

    return global_logger



# async def log_requests(request: Request, call_next):
#     """
#     Middleware function to log incoming requests and their processing time.

#     Args:
#         request (Request): The incoming request.
#         call_next: Function to proceed with request handling.

#     Returns:
#         Response: The response object to be sent back to the client.
#     """
#     logger = setup_logger()  # Ensure logger is properly initialized
#     start_time = time.time()
    
#     try:
#         response = await call_next(request)
#         # Capture response body for logging without affecting the actual response
#         response_body = b""
#         async for chunk in response.body_iterator:
#             response_body += chunk
#         # Reconstruct the response to ensure body is not consumed
#         response = Response(content=response_body, status_code=response.status_code, headers=dict(response.headers), media_type=response.media_type)
#     except HTTPException as e:
#         logger.warning(f"HTTP exception: {e.detail} - Status: {e.status_code}")
#         return JSONResponse(status_code=e.status_code, content={"message": e.detail})
#     except Exception as e:
#         logger.error(f"Unhandled exception: {str(e)}")
#         return JSONResponse(status_code=500, content={"message": "Internal Server Error"})

#     process_time = time.time() - start_time
#     client_host = request.client.host if request.client else "client host unknown"
#     request_line = f'"{request.method} {request.url.path} HTTP/{request.scope["http_version"]}"'

#     # Log response body snippet if present
#     response_body_snippet = response_body.decode('utf-8')[:MAX_RESPONSE_BODY_LOG_LENGTH] + "..." if len(response_body) > MAX_RESPONSE_BODY_LOG_LENGTH else response_body.decode('utf-8')

#     log_message = f"{client_host} - {request_line} {response.status_code} - {process_time:.6f} sec - {response_body_snippet}"

#     logger.info(log_message)
#     return response

async def log_requests(request: Request, call_next):
    """
    Middleware function to log incoming requests and their processing time.

    Args:
        request (Request): The incoming request.
        call_next: Function to proceed with request handling.

    Returns:
        Response: The response object to be sent back to the client.
    """
    logger = setup_logger()  # Ensure logger is properly initialized
    start_time = time.time()

    try:
        response = await call_next(request)

        # Check if the response has a content-type header
        content_type = response.headers.get("content-type", "")
        is_binary_content = not content_type.startswith("text/") and not content_type.startswith("application/json")

        # Capture response body for logging without affecting the actual response
        response_body = b""
        async for chunk in response.body_iterator:
            response_body += chunk

        if is_binary_content:
            # Log binary data without decoding
            response_body_snippet = f"Binary data ({len(response_body)} bytes)"
        else:
            # Log text data with UTF-8 decoding
            response_body_snippet = response_body.decode('utf-8', errors='ignore')[:MAX_RESPONSE_BODY_LOG_LENGTH] + "..." if len(response_body) > MAX_RESPONSE_BODY_LOG_LENGTH else response_body.decode('utf-8', errors='ignore')

        # Reconstruct the response to ensure the body is not consumed
        response = Response(
            content=response_body,
            status_code=response.status_code,
            headers=dict(response.headers),
            media_type=response.media_type
        )
    except HTTPException as e:
        logger.warning(f"HTTP exception: {e.detail} - Status: {e.status_code}")
        return JSONResponse(status_code=e.status_code, content={"message": e.detail})
    except Exception as e:
        logger.error(f"Unhandled exception: {str(e)}")
        return JSONResponse(status_code=500, content={"message": "Internal Server Error"})

    process_time = time.time() - start_time
    client_host = request.client.host if request.client else "client host unknown"
    request_line = f'"{request.method} {request.url.path} HTTP/{request.scope["http_version"]}"'

    log_message = f"{client_host} - {request_line} {response.status_code} - {process_time:.6f} sec - {response_body_snippet}"

    logger.info(log_message)
    return response



def cleanup_old_logs(logs_dir='logs', days_old=30):
    """
    Remove log files older than a specified number of days.

    Args:
        logs_dir (str): Directory containing log files.
        days_old (int): Age threshold in days for log files to be removed.
    """
    current_time = time.time()
    for filename in os.listdir(logs_dir):
        filepath = os.path.join(logs_dir, filename)
        file_creation_time = os.path.getctime(filepath)
        if current_time - file_creation_time > days_old * 86400:  # 86400 seconds in a day
            os.remove(filepath)
            logging.info(f"Removed old log file: {filename}")


async def scheduled_cleanup(logs_dir='logs', days_old=30):
    """
    Run the cleanup task daily at 2 AM to remove old log files.

    Args:
        logs_dir (str): Directory containing log files.
        days_old (int): Age threshold in days for log files to be removed.
    """
    while True:
        now = datetime.now()
        next_run = now.replace(hour=2, minute=0, second=0, microsecond=0) + timedelta(days=1)
        sleep_seconds = (next_run - now).total_seconds()
        logging.info(f"Next cleanup scheduled at {next_run.isoformat()}. "
                     f"Sleeping for {sleep_seconds} seconds.")
        
        await asyncio.sleep(sleep_seconds)  # Sleep until 2 AM
        cleanup_old_logs(logs_dir, days_old)
        await asyncio.sleep(86400)  # Sleep for a day to wait for the next 2 AM
