"""Coding Python SDK - Python client for CODING.net OpenAPI"""

__version__ = "1.0.0"
__author__ = "jjundot"
__all__ = [
    "CodingClient",
    "OAuth2Auth",
    "TokenAuth",
    "BasicAuth",
]

from .client import CodingClient
from .auth import OAuth2Auth, TokenAuth, BasicAuth
