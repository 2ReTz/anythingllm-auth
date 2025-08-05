"""
AnythingLLM Authentication Utilities

A comprehensive Python package for handling authentication with AnythingLLM API.
Supports both Docker and Desktop deployments with sync/async clients.
"""

from .auth import AuthClient, AsyncAuthClient
from .config import Config
from .exceptions import (
    AuthenticationError,
    TokenExpiredError,
    ConfigurationError,
    APIError,
    InstanceDetectionError
)

__version__ = "1.0.0"
__all__ = [
    "AuthClient",
    "AsyncAuthClient",
    "Config",
    "AuthenticationError",
    "TokenExpiredError",
    "ConfigurationError",
    "APIError",
    "InstanceDetectionError"
]