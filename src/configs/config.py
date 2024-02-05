# src/configs/config.py

import os
from dotenv import load_dotenv

# Load .env file if it exists
load_dotenv()

class Config:
    # Base configuration with common settings
    POOL_SIZE = int(os.getenv('POOL_SIZE', 100))
    # Common setting across environments
    MONGO_DB_NAME = os.getenv('MONGO_DB_NAME', 'shopDEV')  # Default for all environments
    
class DevelopmentConfig(Config):
    # Development-specific configurations
    MONGO_CONNECTION_STRING = os.getenv('MONGO_CONNECTION_STRING_DEV', 'mongodb://localhost:27017/dev_db')
    LOG_LEVEL = 'DEBUG'

class ProductionConfig(Config):
    # Production-specific configurations
    MONGO_CONNECTION_STRING = os.getenv('MONGO_CONNECTION_STRING_PROD', 'mongodb://prod_db:27017/prod_db')
    LOG_LEVEL = 'ERROR'

# Dynamic configuration selection based on ENVIRONMENT variable
config_classes = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
}

# Fallback to DevelopmentConfig if environment is not set or not recognized
CurrentConfig = config_classes.get(os.getenv('ENVIRONMENT', 'development').lower(), DevelopmentConfig)
