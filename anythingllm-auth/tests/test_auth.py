#!/usr/bin/env python3
"""
Test suite for AnythingLLM authentication utilities.
"""

import pytest
import asyncio
from unittest.mock import Mock, patch
from anythingllm_auth import AuthClient, AsyncAuthClient, Config
from anythingllm_auth.exceptions import AuthenticationError, APIError


class TestAuthClient:
    """Test cases for synchronous AuthClient."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.config = Config(
            base_url="http://localhost:3001",
            login_endpoint="/auth/login",
            refresh_endpoint="/auth/refresh",
            validate_endpoint="/auth/validate"
        )
    
    @patch('requests.Session.post')
    def test_authenticate_success(self, mock_post):
        """Test successful authentication."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "token": "test_token_123",
            "refreshToken": "test_refresh_456"
        }
        mock_post.return_value = mock_response
        
        client = AuthClient(self.config)
        token = client.authenticate("test_user", "test_pass")
        
        assert token == "test_token_123"
        assert client.token_manager.token == "test_token_123"
        assert client.token_manager.refresh_token == "test_refresh_456"
    
    @patch('requests.Session.post')
    def test_authenticate_invalid_credentials(self, mock_post):
        """Test authentication with invalid credentials."""
        mock_response = Mock()
        mock_response.status_code = 401
        mock_post.return_value = mock_response
        
        client = AuthClient(self.config)
        
        with pytest.raises(AuthenticationError):
            client.authenticate("wrong_user", "wrong_pass")
    
    @patch('requests.Session.post')
    def test_refresh_token_success(self, mock_post):
        """Test successful token refresh."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "token": "new_token_789",
            "refreshToken": "new_refresh_012"
        }
        mock_post.return_value = mock_response
        
        client = AuthClient(self.config)
        client.token_manager.set_tokens("old_token", "old_refresh")
        
        new_token = client.refresh_token()
        
        assert new_token == "new_token_789"
        assert client.token_manager.token == "new_token_789"
    
    @patch('requests.Session.get')
    def test_validate_token_success(self, mock_get):
        """Test successful token validation."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_get.return_value = mock_response
        
        client = AuthClient(self.config)
        client.token_manager.set_tokens("valid_token", "refresh")
        
        is_valid = client.validate_token()
        assert is_valid is True
    
    @patch('requests.Session.get')
    def test_validate_token_invalid(self, mock_get):
        """Test invalid token validation."""
        mock_response = Mock()
        mock_response.status_code = 401
        mock_get.return_value = mock_response
        
        client = AuthClient(self.config)
        client.token_manager.set_tokens("invalid_token", "refresh")
        
        is_valid = client.validate_token()
        assert is_valid is False
    
    def test_close_session(self):
        """Test session cleanup."""
        client = AuthClient(self.config)
        client.close()
        # Should not raise any exceptions


class TestAsyncAuthClient:
    """Test cases for asynchronous AsyncAuthClient."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.config = Config(
            base_url="http://localhost:3001",
            login_endpoint="/auth/login",
            refresh_endpoint="/auth/refresh",
            validate_endpoint="/auth/validate"
        )
    
    @pytest.mark.asyncio
    async def test_async_authenticate_success(self):
        """Test successful async authentication."""
        with patch('aiohttp.ClientSession.post') as mock_post:
            mock_response = Mock()
            mock_response.status = 200
            mock_response.json = asyncio.coroutine(
                lambda: {"token": "async_token_123", "refreshToken": "async_refresh_456"}
            )
            mock_post.return_value.__aenter__.return_value = mock_response
            
            async with AsyncAuthClient(self.config) as client:
                token = await client.authenticate("test_user", "test_pass")
                assert token == "async_token_123"
    
    @pytest.mark.asyncio
    async def test_async_validate_token_success(self):
        """Test successful async token validation."""
        with patch('aiohttp.ClientSession.get') as mock_get:
            mock_response = Mock()
            mock_response.status = 200
            mock_get.return_value.__aenter__.return_value = mock_response
            
            async with AsyncAuthClient(self.config) as client:
                client.token_manager.set_tokens("valid_token", "refresh")
                is_valid = await client.validate_token()
                assert is_valid is True
    
    @pytest.mark.asyncio
    async def test_async_context_manager(self):
        """Test async context manager."""
        async with AsyncAuthClient(self.config) as client:
            assert client.session is not None
        
        # Session should be closed after context
        assert client.session is None


class TestConfig:
    """Test cases for configuration."""
    
    def test_config_from_env(self):
        """Test configuration from environment variables."""
        with patch.dict('os.environ', {
            'ANYTHING_LLM_BASE_URL': 'https://test.example.com',
            'ANYTHING_LLM_TIMEOUT': '45'
        }):
            config = Config.from_env()
            assert config.base_url == 'https://test.example.com'
            assert config.timeout == 45
    
    def test_config_validation(self):
        """Test configuration validation."""
        with pytest.raises(ValueError):
            Config(base_url='invalid-url')
    
    def test_get_full_url(self):
        """Test URL construction."""
        config = Config(base_url='http://localhost:3001')
        full_url = config.get_full_url('test/endpoint')
        assert full_url == 'http://localhost:3001/api/test/endpoint'


if __name__ == "__main__":
    pytest.main([__file__, "-v"])