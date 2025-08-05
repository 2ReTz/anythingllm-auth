#!/usr/bin/env python3
"""
Basic authentication example for AnythingLLM API.

This example demonstrates how to authenticate with AnythingLLM
using the authentication utilities.
"""

import os
import sys
from anythingllm_auth import AuthClient, Config

# Add the parent directory to path so we can import anythingllm_auth
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def main():
    """Main authentication example."""
    print("AnythingLLM Authentication Example")
    print("=" * 40)
    
    # Load configuration from environment
    config = Config.from_env()
    
    # Create authentication client
    auth_client = AuthClient(config)
    
    try:
        # Get credentials from environment or prompt
        username = os.getenv('ANYTHINGLLM_USERNAME')
        password = os.getenv('ANYTHINGLLM_PASSWORD')
        
        if not username:
            username = input("Username: ")
        if not password:
            import getpass
            password = getpass.getpass("Password: ")
        
        print(f"\nAuthenticating with {config.base_url}...")
        
        # Authenticate
        token = auth_client.authenticate(username, password)
        print(f"✓ Authentication successful!")
        print(f"Token: {token[:20]}...")
        
        # Validate token
        is_valid = auth_client.validate_token()
        print(f"✓ Token validation: {'Valid' if is_valid else 'Invalid'}")
        
        # Make an authenticated request to get user info
        print("\nFetching user information...")
        response = auth_client.get('/api/auth/me')
        
        if response.status_code == 200:
            user_info = response.json()
            print(f"✓ User: {user_info.get('username', 'Unknown')}")
            print(f"  Email: {user_info.get('email', 'Not provided')}")
            print(f"  Role: {user_info.get('role', 'Unknown')}")
        else:
            print(f"✗ Failed to get user info: {response.status_code}")
        
        # Test token refresh (if refresh token is available)
        if auth_client.token_manager.refresh_token:
            print("\nTesting token refresh...")
            try:
                new_token = auth_client.refresh_token()
                print(f"✓ Token refreshed successfully")
                print(f"New token: {new_token[:20]}...")
            except Exception as e:
                print(f"✗ Token refresh failed: {e}")
        
    except Exception as e:
        print(f"✗ Error: {e}")
        return 1
    
    finally:
        auth_client.close()
    
    print("\n✓ Example completed successfully!")
    return 0


if __name__ == "__main__":
    sys.exit(main())