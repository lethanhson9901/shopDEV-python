# src/core/success_response_handler.py

class SuccessResponseHandler:
    """
    Handles success responses for API endpoints, providing a unified structure and facilitating
    the easy creation of standardized success responses.
    """

    @staticmethod
    def general_success(data: dict, message: str = "Operation successful", status: int = 200) -> dict:
        """
        Generates a general success response.

        Parameters:
        - data (dict): The data to be included in the response.
        - message (str, optional): A success message. Defaults to "Operation successful".
        - status (int, optional): The HTTP status code. Defaults to 200.

        Returns:
        - dict: The success response.
        """
        return {
            "message": message,
            "data": data,
            "status": status
        }

    @staticmethod
    def user_registered(user_data: dict) -> dict:
        """
        Success response for a newly registered user.

        Parameters:
        - user_data (dict): Data of the registered user.

        Returns:
        - dict: The success response for registration.
        """
        return SuccessResponseHandler.general_success(
            data=user_data,
            message="User signed up successfully",
            status=201
        )
    
    @staticmethod
    def user_authenticated(access_token: str, refresh_token: str, user_role: str) -> dict:
        """
        Success response for an authenticated user.

        Parameters:
        - access_token (str): The JWT access token for the user.
        - refresh_token (str): The JWT refresh token for the user.
        - user_role (str): The role of the authenticated user.

        Returns:
        - dict: The success response for authentication.
        """
        return SuccessResponseHandler.general_success(
            data={
                "access_token": access_token,
                "refresh_token": refresh_token,
                "token_type": "bearer",
                "role": user_role
            },
            message="User authenticated successfully",
            status=200
        )

    @staticmethod
    def password_updated() -> dict:
        """
        Success response for a user's password update.

        Returns:
        - dict: The success response for a password update.
        """
        return SuccessResponseHandler.general_success(
            data={},
            message="Password updated successfully",
            status=200
        )

    @staticmethod
    def paginated_response(data: list, page: int, limit: int, total: int, message: str = "Data retrieved successfully") -> dict:
        """
        Generates a success response for paginated data.

        Parameters:
        - data (list): The list of data items for the current page.
        - page (int): The current page number.
        - limit (int): The number of items per page.
        - total (int): The total number of items across all pages.
        - message (str, optional): A success message. Defaults to "Data retrieved successfully".

        Returns:
        - dict: The paginated success response, including pagination details.
        """
        return {
            "message": message,
            "data": data,
            "pagination": {
                "page": page,
                "limit": limit,
                "total": total,
                "pages": (total + limit - 1) // limit  # Calculate total pages
            },
            "status": 200
        }

    @staticmethod
    def renewed_access_token(access_token: str, refresh_token, role: str) -> dict:
        """
        Success response for renewing an access token.

        Parameters:
        - access_token (str): The newly generated JWT access token.
        - role (str): The role of the user associated with the access token.

        Returns:
        - dict: A dictionary containing the access token, token type, and user role.
        """
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "role": role,
            "message": "Access token renewed successfully",
            "status": 200
        }
