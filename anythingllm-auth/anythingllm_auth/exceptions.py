"""
Custom exceptions for AnythingLLM authentication utilities.
"""


class AnythingLLMAuthError(Exception):
    """Base exception for all AnythingLLM authentication errors."""
    pass


class AuthenticationError(AnythingLLMAuthError):
    """Raised when authentication fails."""
    pass


class TokenExpiredError(AnythingLLMAuthError):
    """Raised when authentication token has expired."""
    pass


class ConfigurationError(AnythingLLMAuthError):
    """Raised when configuration is invalid or missing."""
    pass


class APIError(AnythingLLMAuthError):
    """Raised when API request fails."""
    
    def __init__(self, message, status_code=None, response=None):
        super().__init__(message)
        self.status_code = status_code
        self.response = response


class InstanceDetectionError(AnythingLLMAuthError):
    """Raised when unable to detect instance type (Docker vs Desktop)."""
    pass


class TokenValidationError(AnythingLLMAuthError):
    """Raised when token validation fails."""
    pass