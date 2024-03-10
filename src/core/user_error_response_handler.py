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

    @staticmethod
    def invalid_token(message="Invalid or expired token"):
        """
        Raises an HTTP exception for invalid or expired tokens.

        Parameters:
        - message (str): Custom message detailing the error.

        Returns:
        - Raises an HTTP exception with a 401 status code.
        """
        return ErrorResponseHandler.raise_http_exception(
            status_code=401, detail=message)

    @staticmethod
    def suspicious_activity_detected():
        """
        Raises an HTTP exception for detected suspicious activities, potentially indicating a security issue.
        
        Returns:
        - Raises an HTTP exception with a 403 status code and a custom error message.
        """
        return ErrorResponseHandler.raise_http_exception(
            status_code=403, detail="Suspicious activity detected. Your request cannot be completed.")


    @staticmethod
    def operation_failed(message="An operation failed"):
        """
        Raises an HTTP exception for generic operation failures.

        Parameters:
        - message (str): Custom message detailing the failure.

        Returns:
        - Raises an HTTP exception with a 500 status code.
        """
        return ErrorResponseHandler.raise_http_exception(
            status_code=500, detail=message)