"""
API client module for AnythingLLM authentication utilities.
Provides synchronous and asynchronous clients for interacting with AnythingLLM API.
"""

from typing import Optional, Union
from .auth import AuthClient, AsyncAuthClient
from .config import Config

__all__ = ["AuthClient", "AsyncAuthClient", "create_client", "create_async_client"]


def create_client(config: Optional[Config] = None) -> AuthClient:
    """
    Create a synchronous authentication client.

    Args:
        config: Optional configuration. If not provided, loads from environment.

    Returns:
        AuthClient: Configured synchronous client
    """
    return AuthClient(config)


def create_async_client(config: Optional[Config] = None) -> AsyncAuthClient:
    """
    Create an asynchronous authentication client.

    Args:
        config: Optional configuration. If not provided, loads from environment.

    Returns:
        AsyncAuthClient: Configured asynchronous client
    """
    return AsyncAuthClient(config)


def create_client_from_env(env_file: Optional[str] = None) -> AuthClient:
    """
    Create a synchronous client from environment configuration.

    Args:
        env_file: Optional path to environment file

    Returns:
        AuthClient: Client configured from environment
    """
    config = Config.from_env(env_file)
    return AuthClient(config)


def create_async_client_from_env(env_file: Optional[str] = None) -> AsyncAuthClient:
    """
    Create an asynchronous client from environment configuration.

    Args:
        env_file: Optional path to environment file

    Returns:
        AsyncAuthClient: Client configured from environment
    """
    config = Config.from_env(env_file)
    return AsyncAuthClient(config)