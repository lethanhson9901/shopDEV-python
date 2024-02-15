# src/core/error_response_handler.py

from fastapi import HTTPException
from src.utils.status_codes import STATUS_TEXTS

class ErrorResponseHandler:
    """
    Centralizes the creation of error responses for API endpoints,
    enabling custom details for standard HTTP status codes.
    """

    @classmethod
    def raise_http_exception(cls, status_code: int, detail: str = None):
        """
        Raises an HTTPException with a custom detail or a default message based on the status code.

        Parameters:
        - status_code (int): The HTTP status code for the error.
        - detail (str, optional): The custom error message detail. If None, the default message for the status code is used.
        """
        if not detail:
            # Fallback to a general message if detail is not provided and status code is recognized
            detail = STATUS_TEXTS.get(status_code, "Status Text not defined")
        raise HTTPException(status_code=status_code, detail=detail)

    # Method examples for specific status codes, demonstrating the ability to provide custom details
    @classmethod
    def not_found(cls, detail: str = "Resource not found"):
        cls.raise_http_exception(status_code=404, detail=detail)

    @classmethod
    def bad_request(cls, detail: str = "Bad request"):
        cls.raise_http_exception(status_code=400, detail=detail)

    @classmethod
    def unauthorized(cls, detail: str = "Unauthorized access"):
        cls.raise_http_exception(status_code=401, detail=detail)

    # Additional methods can be added as needed for different error scenarios
