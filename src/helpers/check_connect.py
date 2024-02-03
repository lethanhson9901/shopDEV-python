# src/helpers/check_connect.py

import logging
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo.errors import OperationFailure

# Configure basic logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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
