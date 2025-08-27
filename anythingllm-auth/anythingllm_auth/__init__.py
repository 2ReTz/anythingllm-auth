"""
AnythingLLM Authentication Utilities

A comprehensive Python package for handling authentication with AnythingLLM API.
Supports both Docker and Desktop deployments with sync/async clients.
"""

from .client import AuthClient, AsyncAuthClient, create_client, create_async_client
from .config import Config
from .exceptions import (
    AuthenticationError,
    TokenExpiredError,
    ConfigurationError,
    APIError,
    InstanceDetectionError,
    TokenValidationError
)

__version__ = "1.0.0"
__all__ = [
    "AuthClient",
    "AsyncAuthClient",
    "create_client",
    "create_async_client",
    "Config",
    "AuthenticationError",
    "TokenExpiredError",
    "ConfigurationError",
    "APIError",
    "InstanceDetectionError",
    "TokenValidationError"
]