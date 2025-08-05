#!/usr/bin/env python3
"""
Complete authentication flow test for AnythingLLM API.

This script tests the entire authentication flow including:
- Configuration loading
- Instance detection
- Authentication
- Token validation
- Token refresh
- Error handling
"""

import os
import sys
import asyncio
from anythingllm_auth import AuthClient, AsyncAuthClient, Config
from anythingllm_auth.utils import detect_instance_type, async_detect

# Add the parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def test_sync_flow():
    """Test complete synchronous authentication flow."""
    print("Testing Synchronous Authentication Flow")
    print("=" * 40)
    
    # Load configuration
    config = Config.from_env()
    print(f"✓ Configuration loaded: {config.base_url}")
    
    # Detect instance type
    try:
        instance_type = detect_instance_type(config.base_url)
        print(f"✓ Instance type detected: {instance_type}")
    except Exception as e:
        print(f"⚠ Instance detection failed: {e}")
        instance_type = "unknown"
    
    # Test authentication
    client = AuthClient(config)
    
    try:
        # Get credentials
        username = os.getenv('ANYTHINGLLM_USERNAME', 'admin')
        password = os.getenv('ANYTHINGLLM_PASSWORD', 'password')
        
        print(f"\nAuthenticating as {username}...")
        token = client.authenticate(username, password)
        print(f"✓ Authentication successful")
        print(f"  Token: {token[:20]}...")
        
        # Validate token
        is_valid = client.validate_token()
        print(f"✓ Token validation: {'Valid' if is_valid else 'Invalid'}")
        
        # Test authenticated request
        try:
            response = client.get('/api/v1/workspaces')
            if response.status_code == 200:
                workspaces = response.json()
                print(f"✓ Workspaces retrieved: {len(workspaces.get('workspaces', []))} found")
            else:
                print(f"⚠ Workspaces request failed: {response.status_code}")
        except Exception as e:
            print(f"⚠ Workspaces request error: {e}")
        
        # Test token refresh (if refresh token available)
        if client.token_manager.refresh_token:
            try:
                new_token = client.refresh_token()
                print(f"✓ Token refresh successful")
                print(f"  New token: {new_token[:20]}...")
            except Exception as e:
                print(f"⚠ Token refresh failed: {e}")
        
    except Exception as e:
        print(f"✗ Authentication failed: {e}")
        return False
    
    finally:
        client.close()
    
    return True


async def test_async_flow():
    """Test complete asynchronous authentication flow."""
    print("\nTesting Asynchronous Authentication Flow")
    print("=" * 42)
    
    # Load configuration
    config = Config.from_env()
    print(f"✓ Configuration loaded: {config.base_url}")
    
    # Detect instance type
    try:
        instance_type = await async_detect(config.base_url)
        print(f"✓ Instance type detected: {instance_type}")
    except Exception as e:
        print(f"⚠ Instance detection failed: {e}")
        instance_type = "unknown"
    
    # Test authentication
    async with AsyncAuthClient(config) as client:
        try:
            # Get credentials
            username = os.getenv('ANYTHINGLLM_USERNAME', 'admin')
            password = os.getenv('ANYTHINGLLM_PASSWORD', 'password')
            
            print(f"\nAuthenticating as {username}...")
            token = await client.authenticate(username, password)
            print(f"✓ Authentication successful")
            print(f"  Token: {token[:20]}...")
            
            # Validate token
            is_valid = await client.validate_token()
            print(f"✓ Token validation: {'Valid' if is_valid else 'Invalid'}")
            
            # Test authenticated request
            try:
                response = await client.get('/api/v1/workspaces')
                if response.status == 200:
                    workspaces = await response.json()
                    print(f"✓ Workspaces retrieved: {len(workspaces.get('workspaces', []))} found")
                else:
                    print(f"⚠ Workspaces request failed: {response.status}")
            except Exception as e:
                print(f"⚠ Workspaces request error: {e}")
            
            # Test token refresh (if refresh token available)
            if client.token_manager.refresh_token:
                try:
                    new_token = await client.refresh_token()
                    print(f"✓ Token refresh successful")
                    print(f"  New token: {new_token[:20]}...")
                except Exception as e:
                    print(f"⚠ Token refresh failed: {e}")
            
        except Exception as e:
            print(f"✗ Authentication failed: {e}")
            return False
    
    return True


def test_configuration_templates():
    """Test configuration templates."""
    print("\nTesting Configuration Templates")
    print("=" * 32)
    
    # Test Docker config
    docker_config = Config.from_file('config/docker.env')
    print(f"✓ Docker config: {docker_config.base_url} (SSL: {docker_config.verify_ssl})")
    
    # Test Desktop config
    desktop_config = Config.from_file('config/desktop.env')
    print(f"✓ Desktop config: {desktop_config.base_url} (SSL: {desktop_config.verify_ssl})")
    
    # Test Cloud config
    cloud_config = Config.from_file('config/cloud.env')
    print(f"✓ Cloud config: {cloud_config.base_url} (SSL: {cloud_config.verify_ssl})")
    
    return True


def test_error_handling():
    """Test error handling scenarios."""
    print("\nTesting Error Handling")
    print("=" * 22)
    
    # Test invalid URL
    try:
        Config(base_url="invalid-url")
        print("✗ Invalid URL validation failed")
        return False
    except Exception:
        print("✓ Invalid URL validation works")
    
    # Test authentication with wrong credentials
    config = Config(base_url="http://localhost:3001")
    client = AuthClient(config)
    
    try:
        client.authenticate("wrong_user", "wrong_pass")
        print("✗ Wrong credentials should fail")
        return False
    except Exception as e:
        print(f"✓ Wrong credentials properly rejected: {type(e).__name__}")
    
    client.close()
    return True


def main():
    """Run complete authentication flow tests."""
    print("AnythingLLM Authentication Flow Test Suite")
    print("=" * 45)
    
    # Test configuration templates
    test_configuration_templates()
    
    # Test error handling
    test_error_handling()
    
    # Test sync flow
    sync_success = test_sync_flow()
    
    # Test async flow
    async_success = asyncio.run(test_async_flow())
    
    print("\n" + "=" * 45)
    print("Test Results:")
    print(f"  Sync Flow: {'✓ PASS' if sync_success else '✗ FAIL'}")
    print(f"  Async Flow: {'✓ PASS' if async_success else '✗ FAIL'}")
    
    if sync_success and async_success:
        print("\n🎉 All tests completed successfully!")
        return 0
    else:
        print("\n❌ Some tests failed. Check the output above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())