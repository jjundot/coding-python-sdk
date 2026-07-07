"""Exception classes for Coding SDK"""


class CodingSDKException(Exception):
    """Base exception for Coding SDK"""

    pass


class AuthenticationError(CodingSDKException):
    """Raised when authentication fails"""

    pass


class APIError(CodingSDKException):
    """Raised when API returns an error"""

    def __init__(self, message: str, status_code: int, response_data: dict = None):
        self.message = message
        self.status_code = status_code
        self.response_data = response_data or {}
        super().__init__(f"API Error {status_code}: {message}")


class ValidationError(CodingSDKException):
    """Raised when request validation fails"""

    pass


class NetworkError(CodingSDKException):
    """Raised when network request fails"""

    pass
