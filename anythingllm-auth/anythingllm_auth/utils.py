"""
Utility functions for AnythingLLM authentication utilities.
"""

import base64
import json
import os
import time
import asyncio
from typing import Optional, Dict, Any, Tuple
import requests
import aiohttp
from .config import Config
from .exceptions import InstanceDetectionError


def is_token_expired(token: str, buffer_seconds: int = 300) -> bool:
    """
    Check if a JWT token is expired.
    
    Args:
        token: JWT token string
        buffer_seconds: Buffer time in seconds before actual expiry
        
    Returns:
        bool: True if token is expired or will expire soon
    """
    try:
        # JWT tokens have 3 parts separated by dots
        parts = token.split('.')
        if len(parts) != 3:
            return True
        
        # Decode the payload (second part)
        payload = parts[1]
        # Add padding if needed
        padding = len(payload) % 4
        if padding:
            payload += '=' * (4 - padding)
        
        decoded = base64.urlsafe_b64decode(payload)
        payload_data = json.loads(decoded)
        
        # Check expiry
        exp = payload_data.get('exp')
        if not exp:
            return True
        
        current_time = time.time()
        return current_time + buffer_seconds >= exp
        
    except Exception:
        # If we can't decode the token, assume it's expired
        return True


def format_auth_header(token: str, prefix: str = "Bearer") -> str:
    """
    Format authorization header value.
    
    Args:
        token: Authentication token
        prefix: Token prefix (e.g., "Bearer", "Token")
        
    Returns:
        str: Formatted authorization header value
    """
    return f"{prefix} {token}"


def detect_instance_type(base_url: str, timeout: int = 5) -> str:
    """
    Detect whether AnythingLLM is running as Docker or Desktop.
    
    Args:
        base_url: Base URL of the AnythingLLM instance
        timeout: Request timeout in seconds
        
    Returns:
        str: "docker", "desktop", or "unknown"
        
    Raises:
        InstanceDetectionError: If unable to detect instance type
    """
    try:
        # Try to access health endpoint
        health_url = f"{base_url}/api/health"
        
        response = requests.get(health_url, timeout=timeout)
        
        if response.status_code == 200:
            data = response.json()
            
            # Check for Docker-specific indicators
            if data.get('environment') == 'docker':
                return 'docker'
            elif data.get('environment') == 'desktop':
                return 'desktop'
            
            # Check headers for Docker indicators
            server_header = response.headers.get('Server', '').lower()
            if 'docker' in server_header:
                return 'docker'
            
            # Check for common Docker port mappings
            if ':3001' in base_url:
                return 'docker'
            elif ':3000' in base_url:
                return 'desktop'
        
        # Fallback based on URL patterns
        if 'localhost' in base_url or '127.0.0.1' in base_url:
            if ':3001' in base_url:
                return 'docker'
            elif ':3000' in base_url:
                return 'desktop'
        
        return 'unknown'
        
    except requests.RequestException as e:
        raise InstanceDetectionError(f"Failed to detect instance type: {str(e)}")


async def async_detect(base_url: str, timeout: int = 5) -> str:
    """
    Async version of instance type detection.
    
    Args:
        base_url: Base URL of the AnythingLLM instance
        timeout: Request timeout in seconds
        
    Returns:
        str: "docker", "desktop", or "unknown"
        
    Raises:
        InstanceDetectionError: If unable to detect instance type
    """
    try:
        async with aiohttp.ClientSession() as session:
            health_url = f"{base_url}/api/health"
            
            async with session.get(health_url, timeout=aiohttp.ClientTimeout(total=timeout)) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    # Check for Docker-specific indicators
                    if data.get('environment') == 'docker':
                        return 'docker'
                    elif data.get('environment') == 'desktop':
                        return 'desktop'
                    
                    # Check headers for Docker indicators
                    server_header = response.headers.get('Server', '').lower()
                    if 'docker' in server_header:
                        return 'docker'
                
                # Fallback based on URL patterns
                if 'localhost' in base_url or '127.0.0.1' in base_url:
                    if ':3001' in base_url:
                        return 'docker'
                    elif ':3000' in base_url:
                        return 'desktop'
                
                return 'unknown'
                
    except Exception as e:
        raise InstanceDetectionError(f"Failed to detect instance type: {str(e)}")


def get_default_credentials() -> Tuple[Optional[str], Optional[str]]:
    """
    Get default credentials from environment variables.
    
    Returns:
        Tuple[str, str]: (username, password) or (None, None) if not found
    """
    username = os.getenv('ANYTHING_LLM_USERNAME')
    password = os.getenv('ANYTHING_LLM_PASSWORD')
    return username, password


def create_error_response(error_type: str, message: str, details: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Create standardized error response.
    
    Args:
        error_type: Type of error
        message: Error message
        details: Additional error details
        
    Returns:
        Dict[str, Any]: Standardized error response
    """
    response = {
        "error": {
            "type": error_type,
            "message": message,
            "timestamp": time.time()
        }
    }
    
    if details:
        response["error"]["details"] = details
    
    return response


def retry_with_backoff(func, max_retries: int = 3, delay: float = 1.0, backoff: float = 2.0):
    """
    Retry decorator with exponential backoff.
    
    Args:
        func: Function to retry
        max_retries: Maximum number of retries
        delay: Initial delay in seconds
        backoff: Backoff multiplier
        
    Returns:
        Result of the function call
    """
    import functools
    
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        current_delay = delay
        
        for attempt in range(max_retries + 1):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                if attempt == max_retries:
                    raise
                
                time.sleep(current_delay)
                current_delay *= backoff
        
        return None
    
    return wrapper


async def async_retry_with_backoff(func, max_retries: int = 3, delay: float = 1.0, backoff: float = 2.0):
    """
    Async retry decorator with exponential backoff.
    
    Args:
        func: Async function to retry
        max_retries: Maximum number of retries
        delay: Initial delay in seconds
        backoff: Backoff multiplier
        
    Returns:
        Result of the function call
    """
    current_delay = delay
    
    for attempt in range(max_retries + 1):
        try:
            return await func()
        except Exception as e:
            if attempt == max_retries:
                raise
            
            await asyncio.sleep(current_delay)
            current_delay *= backoff
    
    return None


def validate_url(url: str) -> bool:
    """
    Validate URL format.
    
    Args:
        url: URL to validate
        
    Returns:
        bool: True if URL is valid
    """
    import re
    pattern = r'^https?://(?:[-\w.])+(?:\:\d+)?(?:/(?:[\w/_.])*(?:\?(?:[\w&=%.])*)?(?:#(?:[\w.])*)?)?$'
    return bool(re.match(pattern, url))


def sanitize_input(value: str) -> str:
    """
    Sanitize user input to prevent injection attacks.
    
    Args:
        value: Input value to sanitize
        
    Returns:
        str: Sanitized input
    """
    import html
    return html.escape(str(value).strip())


def mask_token(token: str, visible_chars: int = 4) -> str:
    """
    Mask sensitive token for logging.
    
    Args:
        token: Token to mask
        visible_chars: Number of visible characters at start
        
    Returns:
        str: Masked token
    """
    if not token:
        return ""
    
    if len(token) <= visible_chars:
        return "*" * len(token)
    
    return token[:visible_chars] + "*" * (len(token) - visible_chars)