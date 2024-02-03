# src/helpers/check_connect.py

import logging
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo.errors import OperationFailure
import psutil  # Import psutil for system monitoring

# Configure basic logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Define a constant for the monitoring interval
MONITOR_INTERVAL_SECONDS = 10

async def count_connections(uri):
    """
    Asynchronously count and log the number of active connections to MongoDB.
    
    :param uri: MongoDB URI string
    """
    try:
        async with AsyncIOMotorClient(uri) as client:
            server_status = await client.admin.command("serverStatus")
            connections = server_status['connections']['current']
            logger.info(f"Current MongoDB connections: {connections}")
    except OperationFailure as e:
        logger.error(f"MongoDB operation failed: {e}")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")

async def monitor_system_resources(interval=MONITOR_INTERVAL_SECONDS):
    """
    Monitor system resources (CPU and Memory usage) every `interval` seconds.
    
    :param interval: Interval in seconds between checks
    """
    while True:
        cpu_usage = psutil.cpu_percent(interval=1)  # Ensure fresh CPU usage info
        memory_usage = psutil.virtual_memory().percent
        if cpu_usage > 90 or memory_usage > 90:
            logger.warning(f"System overload detected! CPU: {cpu_usage}%, Memory: {memory_usage}%")
        else:
            logger.info(f"System resources within normal parameters. CPU: {cpu_usage}%, Memory: {memory_usage}%")
        
        await asyncio.sleep(interval)
