# src/helpers/check_connect.py

import logging
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo.errors import OperationFailure
import psutil  # Import psutil for system monitoring
import os

# Configure basic logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Define a constant for the monitoring interval
MONITOR_INTERVAL_SECONDS = 20
URI = os.getenv('MONGO_CONNECTION_STRING')
MAX_POOL_SIZE = os.getenv('POOL_SIZE')

async def count_connections(uri):
    """
    Asynchronously count and log the number of active connections to MongoDB.
    
    :param uri: MongoDB URI string
    """
    client = None  # Initialize client outside of try block
    try:
        client = AsyncIOMotorClient(uri)
        server_status = await client.admin.command("serverStatus")
        connections = server_status['connections']['current']
        logger.info(f"Current MongoDB connections: {connections}")
    except OperationFailure as e:
        logger.error(f"MongoDB operation failed: {e}")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
    finally:
        if client:
            client.close()  # Explicitly close the client without awaiting


async def monitor_system_resources(uri=URI, interval=MONITOR_INTERVAL_SECONDS):
    """
    Monitor system resources (CPU and Memory usage) and MongoDB connections every `interval` seconds.
    
    :param uri: MongoDB URI string
    :param interval: Interval in seconds between checks
    """
    while True:
        # Check system resources
        cpu_usage = psutil.cpu_percent(interval=1)  # Ensure fresh CPU usage info
        memory_usage = psutil.virtual_memory().percent
        if cpu_usage > 90 or memory_usage > 90:
            logger.warning(f"System overload detected! CPU: {cpu_usage}%, Memory: {memory_usage}%")
        else:
            logger.info(f"System resources within normal parameters. CPU: {cpu_usage}%, Memory: {memory_usage}%")
        
        # Now check MongoDB connections within the same loop
        connections = await count_connections(uri)
        if connections is not None:  # Only log if count_connections succeeded
            if connections < MAX_POOL_SIZE:
                logger.info(f"Monitored MongoDB connections: {connections}")    
            else:
                logger.critical(f"Number of connections ({connections}) exceeds max pool size ({MAX_POOL_SIZE}). Consider increasing the pool size or implementing connection throttling.")
            
        await asyncio.sleep(interval)  # Sleep at the end of the loop for the specified interval

