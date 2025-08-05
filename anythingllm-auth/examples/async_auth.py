#!/usr/bin/env python3
"""
Asynchronous authentication example for AnythingLLM API.

This example demonstrates how to use the async authentication client
with proper async/await patterns.
"""

import asyncio
import os
import sys
from anythingllm_auth import AsyncAuthClient, Config

# Add the parent directory to path so we can import anythingllm_auth
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


async def main():
    """Main async authentication example."""
    print("Async AnythingLLM Authentication Example")
    print("=" * 45)
    
    # Load configuration from environment
    config = Config.from_env()
    
    async with AsyncAuthClient(config) as auth_client:
        try:
            # Get credentials from environment
            username = os.getenv('ANYTHINGLLM_USERNAME', 'admin')
            password = os.getenv('ANYTHINGLLM_PASSWORD', 'password')
            
            print(f"\nAuthenticating with {config.base_url}...")
            
            # Authenticate
            token = await auth_client.authenticate(username, password)
            print(f"✓ Authentication successful!")
            print(f"Token: {token[:20]}...")
            
            # Validate token
            is_valid = await auth_client.validate_token()
            print(f"✓ Token validation: {'Valid' if is_valid else 'Invalid'}")
            
            # Make concurrent authenticated requests
            print("\nMaking concurrent API calls...")
            
            # Get user info
            user_response = await auth_client.get('/api/auth/me')
            if user_response.status == 200:
                user_info = await user_response.json()
                print(f"✓ User: {user_info.get('username', 'Unknown')}")
            
            # Get workspace info
            workspace_response = await auth_client.get('/api/v1/workspaces')
            if workspace_response.status == 200:
                workspaces = await workspace_response.json()
                print(f"✓ Workspaces: {len(workspaces.get('workspaces', []))} found")
            
            # Test token refresh
            if auth_client.token_manager.refresh_token:
                print("\nTesting async token refresh...")
                try:
                    new_token = await auth_client.refresh_token()
                    print(f"✓ Token refreshed successfully")
                    print(f"New token: {new_token[:20]}...")
                except Exception as e:
                    print(f"✗ Token refresh failed: {e}")
            
        except Exception as e:
            print(f"✗ Error: {e}")
            return 1
    
    print("\n✓ Async example completed successfully!")
    return 0


if __name__ == "__main__":
    asyncio.run(main())