#!/usr/bin/env python3
"""
Configuration template examples for different deployment types.

This example shows how to use configuration templates for
Docker, Desktop, and custom deployments.
"""

import os
import sys
from anythingllm_auth import Config

# Add the parent directory to path so we can import anythingllm_auth
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def create_docker_config():
    """Create Docker configuration."""
    print("Docker Configuration Template")
    print("=" * 30)
    
    config = Config(
        base_url="http://localhost:3001",
        login_endpoint="/api/auth/login",
        refresh_endpoint="/api/auth/refresh",
        validate_endpoint="/api/auth/validate",
        timeout=30,
        verify_ssl=False  # Often disabled in Docker for development
    )
    
    print("Docker .env file:")
    print("ANYTHING_LLM_BASE_URL=http://localhost:3001")
    print("ANYTHING_LLM_TIMEOUT=30")
    print("ANYTHING_LLM_VERIFY_SSL=false")
    print("ANYTHING_LLM_DOCKER=true")
    
    return config


def create_desktop_config():
    """Create Desktop configuration."""
    print("\nDesktop Configuration Template")
    print("=" * 32)
    
    config = Config(
        base_url="http://localhost:3001",
        login_endpoint="/api/auth/login",
        refresh_endpoint="/api/auth/refresh",
        validate_endpoint="/api/auth/validate",
        timeout=60,  # Desktop might be slower
        verify_ssl=True
    )
    
    print("Desktop .env file:")
    print("ANYTHING_LLM_BASE_URL=http://localhost:3001")
    print("ANYTHING_LLM_TIMEOUT=60")
    print("ANYTHING_LLM_VERIFY_SSL=true")
    print("ANYTHING_LLM_DESKTOP=true")
    
    return config


def create_cloud_config():
    """Create Cloud configuration."""
    print("\nCloud Configuration Template")
    print("=" * 30)
    
    config = Config(
        base_url="https://anythingllm.example.com",
        login_endpoint="/api/auth/login",
        refresh_endpoint="/api/auth/refresh",
        validate_endpoint="/api/auth/validate",
        timeout=30,
        verify_ssl=True,
        max_retries=3,
        retry_delay=2.0
    )
    
    print("Cloud .env file:")
    print("ANYTHING_LLM_BASE_URL=https://anythingllm.example.com")
    print("ANYTHING_LLM_TIMEOUT=30")
    print("ANYTHING_LLM_VERIFY_SSL=true")
    print("ANYTHING_LLM_MAX_RETRIES=3")
    print("ANYTHING_LLM_RETRY_DELAY=2.0")
    
    return config


def create_custom_config():
    """Create custom configuration."""
    print("\nCustom Configuration Example")
    print("=" * 28)
    
    # Load from custom .env file
    custom_env_path = os.path.join(os.path.dirname(__file__), 'custom.env')
    
    if os.path.exists(custom_env_path):
        config = Config.from_file(custom_env_path)
        print(f"Loaded custom config from: {custom_env_path}")
    else:
        config = Config(
            base_url="http://custom-host:8080",
            login_endpoint="/custom-auth/login",
            refresh_endpoint="/custom-auth/refresh",
            validate_endpoint="/custom-auth/validate",
            token_header="X-API-Key",
            token_prefix="Token"
        )
        print("Using programmatic custom config")
    
    print(f"Base URL: {config.base_url}")
    print(f"Login Endpoint: {config.login_endpoint}")
    print(f"Token Header: {config.token_header}")
    
    return config


def main():
    """Main configuration template example."""
    print("AnythingLLM Configuration Templates")
    print("=" * 35)
    
    # Create different configurations
    docker_config = create_docker_config()
    desktop_config = create_desktop_config()
    cloud_config = create_cloud_config()
    custom_config = create_custom_config()
    
    # Compare configurations
    print("\nConfiguration Comparison:")
    print("-" * 25)
    
    configs = {
        "Docker": docker_config,
        "Desktop": desktop_config,
        "Cloud": cloud_config,
        "Custom": custom_config
    }
    
    for name, config in configs.items():
        print(f"{name:8} -> {config.base_url} (SSL: {config.verify_ssl})")
    
    # Save example .env files
    print("\nSaving example .env files...")
    
    env_templates = {
        "docker.env": docker_config,
        "desktop.env": desktop_config,
        "cloud.env": cloud_config
    }
    
    for filename, config in env_templates.items():
        filepath = os.path.join(os.path.dirname(__file__), '..', 'config', filename)
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        
        with open(filepath, 'w') as f:
            f.write(f"# AnythingLLM {filename.replace('.env', '').title()} Configuration\n")
            f.write(f"ANYTHING_LLM_BASE_URL={config.base_url}\n")
            f.write(f"ANYTHING_LLM_TIMEOUT={config.timeout}\n")
            f.write(f"ANYTHING_LLM_VERIFY_SSL={str(config.verify_ssl).lower()}\n")
            f.write(f"ANYTHING_LLM_MAX_RETRIES={config.max_retries}\n")
            f.write(f"ANYTHING_LLM_RETRY_DELAY={config.retry_delay}\n")
            
            if 'docker' in filename:
                f.write("ANYTHING_LLM_DOCKER=true\n")
            elif 'desktop' in filename:
                f.write("ANYTHING_LLM_DESKTOP=true\n")
    
    print("✓ Configuration templates saved to config/ directory")


if __name__ == "__main__":
    main()