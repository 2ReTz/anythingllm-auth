"""
Configuration management for AnythingLLM authentication utilities.
"""

import os
from typing import Optional, Dict, Any
from pathlib import Path
from dotenv import load_dotenv
from pydantic import BaseModel, Field, validator
from .exceptions import ConfigurationError


class Config(BaseModel):
    """Configuration model for AnythingLLM authentication."""
    
    # Base URL configuration
    base_url: str = Field(default="http://localhost:3001")
    api_prefix: str = Field(default="/api")
    
    # Authentication endpoints
    login_endpoint: str = Field(default="/auth/login")
    refresh_endpoint: str = Field(default="/auth/refresh")
    validate_endpoint: str = Field(default="/auth/validate")
    
    # Token configuration
    token_header: str = Field(default="Authorization")
    token_prefix: str = Field(default="Bearer")
    token_expiry_buffer: int = Field(default=300)  # 5 minutes
    
    # Instance detection
    docker_env_var: str = Field(default="ANYTHING_LLM_DOCKER")
    desktop_env_var: str = Field(default="ANYTHING_LLM_DESKTOP")
    
    # Default credentials (for development/testing)
    default_username: Optional[str] = None
    default_password: Optional[str] = None
    
    # Request configuration
    timeout: int = Field(default=30)
    max_retries: int = Field(default=3)
    retry_delay: float = Field(default=1.0)
    
    # SSL/TLS
    verify_ssl: bool = Field(default=True)
    
    class Config:
        env_prefix = "ANYTHING_LLM_"
        case_sensitive = False
    
    @validator('base_url')
    def validate_base_url(cls, v):
        """Validate base URL format."""
        if not v.startswith(('http://', 'https://')):
            raise ConfigurationError("base_url must start with http:// or https://")
        return v.rstrip('/')
    
    @validator('timeout')
    def validate_timeout(cls, v):
        """Validate timeout is positive."""
        if v <= 0:
            raise ConfigurationError("timeout must be positive")
        return v
    
    @classmethod
    def from_env(cls, env_file: Optional[str] = None) -> 'Config':
        """Create configuration from environment variables."""
        if env_file and os.path.exists(env_file):
            load_dotenv(env_file)
        
        # Load from environment with prefix
        env_vars = {}
        for key, value in os.environ.items():
            if key.startswith(cls.Config.env_prefix):
                config_key = key[len(cls.Config.env_prefix):].lower()
                env_vars[config_key] = value
        
        return cls(**env_vars)
    
    @classmethod
    def from_file(cls, config_path: str) -> 'Config':
        """Load configuration from a file."""
        config_path = Path(config_path)
        if not config_path.exists():
            raise ConfigurationError(f"Config file not found: {config_path}")
        
        if config_path.suffix.lower() == '.env':
            return cls.from_env(str(config_path))
        
        raise ConfigurationError(f"Unsupported config file format: {config_path.suffix}")
    
    def get_full_url(self, endpoint: str) -> str:
        """Get full URL for an endpoint."""
        endpoint = endpoint.lstrip('/')
        api_prefix = self.api_prefix.strip('/')
        return f"{self.base_url}/{api_prefix}/{endpoint}"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary."""
        return self.dict()