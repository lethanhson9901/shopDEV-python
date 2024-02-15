# src/core/user_error_response_handler.py
from src.core.error_response_handler import ErrorResponseHandler

class UserErrorResponseHandler(ErrorResponseHandler):
    """
    Handles specific error scenarios encountered in user services, providing detailed error messages.
    """

    @staticmethod
    def email_already_registered():
        return ErrorResponseHandler.raise_http_exception(
            status_code=409, detail="Email already registered")

    @staticmethod
    def incorrect_email_or_password():
        return ErrorResponseHandler.raise_http_exception(
            status_code=401, detail="Incorrect email or password")

    @staticmethod
    def password_update_error():
        return ErrorResponseHandler.raise_http_exception(
            status_code=500, detail="An error occurred during the password update process")

    @staticmethod
    def user_not_found():
        return ErrorResponseHandler.raise_http_exception(
            status_code=404, detail="User not found")

    @staticmethod
    def password_reset_failed():
        return ErrorResponseHandler.raise_http_exception(
            status_code=500, detail="Failed to send password reset email")
