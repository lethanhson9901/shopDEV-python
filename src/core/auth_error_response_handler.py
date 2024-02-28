# src/core/auth_error_response_handler.py

from src.core.error_response_handler import ErrorResponseHandler

class AuthErrorResponseHandler(ErrorResponseHandler):
    """
    Handles specific error scenarios encountered in authentication processes, providing detailed error messages.
    """

    @staticmethod
    def missing_authorization_header():
        """Raises an exception for missing Authorization header."""
        return ErrorResponseHandler.raise_http_exception(
            status_code=401, detail="Authorization header is missing")

    @staticmethod
    def invalid_authentication_scheme():
        """Raises an exception for invalid authentication scheme."""
        return ErrorResponseHandler.raise_http_exception(
            status_code=401, detail="Invalid authentication scheme")

    @staticmethod
    def token_missing():
        """Raises an exception for missing token."""
        return ErrorResponseHandler.raise_http_exception(
            status_code=401, detail="Token is missing")

    @staticmethod
    def invalid_authorization_header_format():
        """Raises an exception for invalid Authorization header format."""
        return ErrorResponseHandler.raise_http_exception(
            status_code=401, detail="Invalid Authorization header format")

    @staticmethod
    def credentials_validation_failed():
        """Raises an exception for failed credentials validation."""
        return ErrorResponseHandler.raise_http_exception(
            status_code=401, detail="Could not validate credentials")

    @staticmethod
    def user_id_extraction_failed():
        """Raises an exception for failed user ID extraction from token."""
        return ErrorResponseHandler.raise_http_exception(
            status_code=401, detail="Could not extract user ID from token")

    @staticmethod
    def key_information_not_found():
        """Raises an exception when key information is not found."""
        return ErrorResponseHandler.raise_http_exception(
            status_code=404, detail="Key information not found")

    @staticmethod
    def invalid_or_expired_token(message="Invalid or expired token"):
        """
        Raises an HTTP exception for invalid or expired tokens with a customizable message.

        Parameters:
        - message (str): Custom message detailing the error.

        Returns:
        - Raises an HTTP exception with a 401 status code.
        """
        return ErrorResponseHandler.raise_http_exception(
            status_code=401, detail=message)
