import os
from dotenv import load_dotenv
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization

# Load .env file if it exists
load_dotenv()

class Config:
    ALGORITHM = os.getenv('ALGORITHM', 'HS256')
    PRIVATE_KEY_PATH = os.getenv('PRIVATE_KEY_PATH', None)
    PUBLIC_KEY_PATH = os.getenv('PUBLIC_KEY_PATH', None)
    PRIVATE_KEY = os.getenv('PRIVATE_KEY', None)  # Directly use the key value from env
    PUBLIC_KEY = os.getenv('PUBLIC_KEY', None)  # Directly use the key value from env
    ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv('ACCESS_TOKEN_EXPIRE_MINUTES', 30))
    REFRESH_TOKEN_EXPIRE_MINUTES = int(os.getenv('REFRESH_TOKEN_EXPIRE_MINUTES', 43200))
    POOL_SIZE = int(os.getenv('POOL_SIZE', 100))
    MONGO_DB_NAME = os.getenv('MONGO_DB_NAME', 'shopDEV')  # Default for all environments
    
    @staticmethod
    def load_private_key():
        try:
            if Config.PRIVATE_KEY_PATH:
                with open(Config.PRIVATE_KEY_PATH, "rb") as key_file:
                    private_key = serialization.load_pem_private_key(
                        key_file.read(),
                        password=None,
                        backend=default_backend()
                    )
                    # Convert the key to PEM format as a string
                    pem_private_key = private_key.private_bytes(
                        encoding=serialization.Encoding.PEM,
                        format=serialization.PrivateFormat.PKCS8,
                        encryption_algorithm=serialization.NoEncryption()
                    )
                    return pem_private_key.decode('utf-8')
        except FileNotFoundError:
            print("Private key file not found, attempting to use the direct key value.")
        if Config.PRIVATE_KEY:
            # Assuming PRIVATE_KEY is already a PEM-encoded string in the environment
            return Config.PRIVATE_KEY
        return None

    @staticmethod
    def load_public_key():
        try:
            if Config.PUBLIC_KEY_PATH:
                with open(Config.PUBLIC_KEY_PATH, "rb") as key_file:
                    public_key = serialization.load_pem_public_key(
                        key_file.read(),
                        backend=default_backend()
                    )
                    # Convert the key to PEM format as a string
                    pem_public_key = public_key.public_bytes(
                        encoding=serialization.Encoding.PEM,
                        format=serialization.PublicFormat.SubjectPublicKeyInfo
                    )
                    return pem_public_key.decode('utf-8')
        except FileNotFoundError:
            print("Public key file not found, attempting to use the direct key value.")
        if Config.PUBLIC_KEY:
            # Assuming PUBLIC_KEY is already a PEM-encoded string in the environment
            return Config.PUBLIC_KEY
        return None
    
class DevelopmentConfig(Config):
    # Development-specific configurations
    MONGO_CONNECTION_STRING = os.getenv('MONGO_CONNECTION_STRING_DEV', 'mongodb://localhost:27017/dev_db')
    LOG_LEVEL = 'DEBUG'

class ProductionConfig(Config):
    # Production-specific configurations
    MONGO_CONNECTION_STRING = os.getenv('MONGO_CONNECTION_STRING_PROD', 'mongodb://user:password@prod_db:27017/prod_db')
    LOG_LEVEL = 'ERROR'

# Dynamic configuration selection based on ENVIRONMENT variable
config_classes = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
}

# Fallback to DevelopmentConfig if environment is not set or not recognized
CurrentConfig = config_classes.get(os.getenv('ENVIRONMENT', 'development').lower(), DevelopmentConfig)
