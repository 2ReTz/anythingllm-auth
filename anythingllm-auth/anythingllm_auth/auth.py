"""
Main authentication module for AnythingLLM API.
"""

import json
import time
from typing import Optional, Dict, Any, Tuple
import requests
import aiohttp
from .config import Config
from .exceptions import (
    AuthenticationError,
    TokenExpiredError,
    APIError,
    TokenValidationError
)
from .utils import is_token_expired, format_auth_header


class TokenManager:
    """Manages authentication tokens."""
    
    def __init__(self, config: Config):
        self.config = config
        self._token: Optional[str] = None
        self._refresh_token: Optional[str] = None
        self._token_expires_at: Optional[float] = None
        self._user_info: Optional[Dict[str, Any]] = None
    
    @property
    def token(self) -> Optional[str]:
        """Get current token."""
        return self._token
    
    @property
    def refresh_token(self) -> Optional[str]:
        """Get refresh token."""
        return self._refresh_token
    
    @property
    def is_authenticated(self) -> bool:
        """Check if currently authenticated."""
        return self._token is not None and not self.is_token_expired
    
    @property
    def is_token_expired(self) -> bool:
        """Check if current token is expired."""
        if not self._token:
            return True
        return is_token_expired(self._token, self.config.token_expiry_buffer)
    
    def set_tokens(self, token: str, refresh_token: Optional[str] = None):
        """Set authentication tokens."""
        self._token = token
        self._refresh_token = refresh_token
    
    def clear_tokens(self):
        """Clear all tokens."""
        self._token = None
        self._refresh_token = None
        self._token_expires_at = None
        self._user_info = None


class AuthClient:
    """Synchronous authentication client for AnythingLLM API."""
    
    def __init__(self, config: Optional[Config] = None):
        self.config = config or Config.from_env()
        self.token_manager = TokenManager(self.config)
        self.session = requests.Session()
        self.session.verify = self.config.verify_ssl
        self.session.timeout = self.config.timeout
    
    def authenticate(self, username: str, password: str) -> str:
        """
        Authenticate with username and password.
        
        Args:
            username: Username for authentication
            password: Password for authentication
            
        Returns:
            str: Authentication token
            
        Raises:
            AuthenticationError: If authentication fails
            APIError: If API request fails
        """
        url = self.config.get_full_url(self.config.login_endpoint)
        
        payload = {
            "username": username,
            "password": password
        }
        
        try:
            response = self.session.post(
                url,
                json=payload,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                data = response.json()
                token = data.get("token")
                refresh_token = data.get("refreshToken")
                
                if not token:
                    raise AuthenticationError("No token received in response")
                
                self.token_manager.set_tokens(token, refresh_token)
                return token
                
            elif response.status_code == 401:
                raise AuthenticationError("Invalid username or password")
            else:
                raise APIError(
                    f"Authentication failed with status {response.status_code}",
                    status_code=response.status_code,
                    response=response
                )
                
        except requests.RequestException as e:
            raise APIError(f"Failed to authenticate: {str(e)}")
    
    def refresh_token(self) -> str:
        """
        Refresh authentication token using refresh token.
        
        Returns:
            str: New authentication token
            
        Raises:
            AuthenticationError: If refresh fails
            APIError: If API request fails
        """
        if not self.token_manager.refresh_token:
            raise AuthenticationError("No refresh token available")
        
        url = self.config.get_full_url(self.config.refresh_endpoint)
        
        payload = {
            "refreshToken": self.token_manager.refresh_token
        }
        
        try:
            response = self.session.post(
                url,
                json=payload,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                data = response.json()
                token = data.get("token")
                refresh_token = data.get("refreshToken", self.token_manager.refresh_token)
                
                if not token:
                    raise AuthenticationError("No token received in refresh response")
                
                self.token_manager.set_tokens(token, refresh_token)
                return token
                
            elif response.status_code == 401:
                raise AuthenticationError("Refresh token expired or invalid")
            else:
                raise APIError(
                    f"Token refresh failed with status {response.status_code}",
                    status_code=response.status_code,
                    response=response
                )
                
        except requests.RequestException as e:
            raise APIError(f"Failed to refresh token: {str(e)}")
    
    def validate_token(self, token: Optional[str] = None) -> bool:
        """
        Validate authentication token.
        
        Args:
            token: Token to validate (uses current token if None)
            
        Returns:
            bool: True if token is valid
            
        Raises:
            TokenValidationError: If validation fails
        """
        check_token = token or self.token_manager.token
        
        if not check_token:
            return False
        
        url = self.config.get_full_url(self.config.validate_endpoint)
        
        headers = {
            self.config.token_header: format_auth_header(
                check_token, 
                self.config.token_prefix
            )
        }
        
        try:
            response = self.session.get(url, headers=headers)
            
            if response.status_code == 200:
                return True
            elif response.status_code == 401:
                return False
            else:
                raise TokenValidationError(
                    f"Token validation failed with status {response.status_code}"
                )
                
        except requests.RequestException as e:
            raise TokenValidationError(f"Failed to validate token: {str(e)}")
    
    def ensure_valid_token(self) -> str:
        """
        Ensure we have a valid token, refreshing if necessary.
        
        Returns:
            str: Valid authentication token
            
        Raises:
            AuthenticationError: If token cannot be validated or refreshed
        """
        if not self.token_manager.token:
            raise AuthenticationError("No token available")
        
        if not self.token_manager.is_token_expired:
            return self.token_manager.token
        
        try:
            return self.refresh_token()
        except AuthenticationError:
            raise AuthenticationError("Token expired and refresh failed")
    
    def make_authenticated_request(
        self,
        method: str,
        endpoint: str,
        **kwargs
    ) -> requests.Response:
        """
        Make an authenticated API request.
        
        Args:
            method: HTTP method
            endpoint: API endpoint
            **kwargs: Additional arguments for requests
            
        Returns:
            requests.Response: API response
            
        Raises:
            AuthenticationError: If authentication fails
            APIError: If API request fails
        """
        token = self.ensure_valid_token()
        
        url = self.config.get_full_url(endpoint)
        
        headers = kwargs.pop('headers', {})
        headers[self.config.token_header] = format_auth_header(
            token,
            self.config.token_prefix
        )
        
        try:
            response = self.session.request(
                method,
                url,
                headers=headers,
                **kwargs
            )
            
            if response.status_code == 401:
                # Token might have expired, try to refresh
                try:
                    token = self.refresh_token()
                    headers[self.config.token_header] = format_auth_header(
                        token,
                        self.config.token_prefix
                    )
                    response = self.session.request(
                        method,
                        url,
                        headers=headers,
                        **kwargs
                    )
                except AuthenticationError:
                    raise AuthenticationError("Authentication expired")
            
            return response
            
        except requests.RequestException as e:
            raise APIError(f"API request failed: {str(e)}")
    
    def get(self, endpoint: str, **kwargs) -> requests.Response:
        """Make authenticated GET request."""
        return self.make_authenticated_request('GET', endpoint, **kwargs)
    
    def post(self, endpoint: str, **kwargs) -> requests.Response:
        """Make authenticated POST request."""
        return self.make_authenticated_request('POST', endpoint, **kwargs)
    
    def put(self, endpoint: str, **kwargs) -> requests.Response:
        """Make authenticated PUT request."""
        return self.make_authenticated_request('PUT', endpoint, **kwargs)
    
    def delete(self, endpoint: str, **kwargs) -> requests.Response:
        """Make authenticated DELETE request."""
        return self.make_authenticated_request('DELETE', endpoint, **kwargs)
    
    def close(self):
        """Close the session."""
        self.session.close()


class AsyncAuthClient:
    """Asynchronous authentication client for AnythingLLM API."""
    
    def __init__(self, config: Optional[Config] = None):
        self.config = config or Config.from_env()
        self.token_manager = TokenManager(self.config)
        self.session: Optional[aiohttp.ClientSession] = None
    
    async def __aenter__(self):
        """Async context manager entry."""
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=self.config.timeout),
            connector=aiohttp.TCPConnector(verify_ssl=self.config.verify_ssl)
        )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        if self.session:
            await self.session.close()
    
    async def _get_session(self) -> aiohttp.ClientSession:
        """Get or create aiohttp session."""
        if not self.session:
            self.session = aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=self.config.timeout),
                connector=aiohttp.TCPConnector(verify_ssl=self.config.verify_ssl)
            )
        return self.session
    
    async def authenticate(self, username: str, password: str) -> str:
        """Async authenticate with username and password."""
        session = await self._get_session()
        url = self.config.get_full_url(self.config.login_endpoint)
        
        payload = {
            "username": username,
            "password": password
        }
        
        try:
            async with session.post(
                url,
                json=payload,
                headers={"Content-Type": "application/json"}
            ) as response:
                
                if response.status == 200:
                    data = await response.json()
                    token = data.get("token")
                    refresh_token = data.get("refreshToken")
                    
                    if not token:
                        raise AuthenticationError("No token received in response")
                    
                    self.token_manager.set_tokens(token, refresh_token)
                    return token
                    
                elif response.status == 401:
                    raise AuthenticationError("Invalid username or password")
                else:
                    text = await response.text()
                    raise APIError(
                        f"Authentication failed with status {response.status}",
                        status_code=response.status,
                        response=text
                    )
                    
        except aiohttp.ClientError as e:
            raise APIError(f"Failed to authenticate: {str(e)}")
    
    async def refresh_token(self) -> str:
        """Async refresh authentication token."""
        if not self.token_manager.refresh_token:
            raise AuthenticationError("No refresh token available")
        
        session = await self._get_session()
        url = self.config.get_full_url(self.config.refresh_endpoint)
        
        payload = {
            "refreshToken": self.token_manager.refresh_token
        }
        
        try:
            async with session.post(
                url,
                json=payload,
                headers={"Content-Type": "application/json"}
            ) as response:
                
                if response.status == 200:
                    data = await response.json()
                    token = data.get("token")
                    refresh_token = data.get("refreshToken", self.token_manager.refresh_token)
                    
                    if not token:
                        raise AuthenticationError("No token received in refresh response")
                    
                    self.token_manager.set_tokens(token, refresh_token)
                    return token
                    
                elif response.status == 401:
                    raise AuthenticationError("Refresh token expired or invalid")
                else:
                    text = await response.text()
                    raise APIError(
                        f"Token refresh failed with status {response.status}",
                        status_code=response.status,
                        response=text
                    )
                    
        except aiohttp.ClientError as e:
            raise APIError(f"Failed to refresh token: {str(e)}")
    
    async def validate_token(self, token: Optional[str] = None) -> bool:
        """Async validate authentication token."""
        check_token = token or self.token_manager.token
        
        if not check_token:
            return False
        
        session = await self._get_session()
        url = self.config.get_full_url(self.config.validate_endpoint)
        
        headers = {
            self.config.token_header: format_auth_header(
                check_token,
                self.config.token_prefix
            )
        }
        
        try:
            async with session.get(url, headers=headers) as response:
                if response.status == 200:
                    return True
                elif response.status == 401:
                    return False
                else:
                    text = await response.text()
                    raise TokenValidationError(
                        f"Token validation failed with status {response.status}: {text}"
                    )
                    
        except aiohttp.ClientError as e:
            raise TokenValidationError(f"Failed to validate token: {str(e)}")
    
    async def ensure_valid_token(self) -> str:
        """Async ensure we have a valid token."""
        if not self.token_manager.token:
            raise AuthenticationError("No token available")
        
        if not self.token_manager.is_token_expired:
            return self.token_manager.token
        
        try:
            return await self.refresh_token()
        except AuthenticationError:
            raise AuthenticationError("Token expired and refresh failed")
    
    async def make_authenticated_request(
        self,
        method: str,
        endpoint: str,
        **kwargs
    ) -> aiohttp.ClientResponse:
        """Make an async authenticated API request."""
        token = await self.ensure_valid_token()
        
        session = await self._get_session()
        url = self.config.get_full_url(endpoint)
        
        headers = kwargs.pop('headers', {})
        headers[self.config.token_header] = format_auth_header(
            token,
            self.config.token_prefix
        )
        
        try:
            response = await session.request(
                method,
                url,
                headers=headers,
                **kwargs
            )
            
            if response.status == 401:
                # Try to refresh token and retry
                try:
                    token = await self.refresh_token()
                    headers[self.config.token_header] = format_auth_header(
                        token,
                        self.config.token_prefix
                    )
                    response = await session.request(
                        method,
                        url,
                        headers=headers,
                        **kwargs
                    )
                except AuthenticationError:
                    raise AuthenticationError("Authentication expired")
            
            return response
            
        except aiohttp.ClientError as e:
            raise APIError(f"API request failed: {str(e)}")
    
    async def get(self, endpoint: str, **kwargs) -> aiohttp.ClientResponse:
        """Make authenticated async GET request."""
        return await self.make_authenticated_request('GET', endpoint, **kwargs)
    
    async def post(self, endpoint: str, **kwargs) -> aiohttp.ClientResponse:
        """Make authenticated async POST request."""
        return await self.make_authenticated_request('POST', endpoint, **kwargs)
    
    async def put(self, endpoint: str, **kwargs) -> aiohttp.ClientResponse:
        """Make authenticated async PUT request."""
        return await self.make_authenticated_request('PUT', endpoint, **kwargs)
    
    async def delete(self, endpoint: str, **kwargs) -> aiohttp.ClientResponse:
        """Make authenticated async DELETE request."""
        return await self.make_authenticated_request('DELETE', endpoint, **kwargs)
    
    async def close(self):
        """Close the async session."""
        if self.session:
            await self.session.close()
            self.session = None