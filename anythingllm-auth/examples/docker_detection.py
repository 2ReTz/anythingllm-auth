#!/usr/bin/env python3
"""
Docker vs Desktop detection example for AnythingLLM.

This example demonstrates how to detect whether AnythingLLM
is running as a Docker container or desktop application.
"""

import os
import sys
import asyncio
from anythingllm_auth import Config
from anythingllm_auth.utils import detect_instance_type, async_detect

# Add the parent directory to path so we can import anythingllm_auth
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def sync_detection_example():
    """Synchronous detection example."""
    print("Synchronous Docker/Desktop Detection")
    print("=" * 40)
    
    # Create config with auto-detection
    config = Config.from_env()
    
    print(f"Base URL: {config.base_url}")
    print(f"Instance Type: {config.instance_type}")
    print(f"Docker Mode: {config.docker_mode}")
    
    # Manual detection
    print("\nManual Detection:")
    instance_type = detect_instance_type(config.base_url)
    print(f"Detected: {instance_type}")
    
    # Test different URLs
    test_urls = [
        "http://localhost:3001",
        "http://localhost:3000",
        "http://anythingllm:3001",
        "https://anythingllm.example.com"
    ]
    
    print("\nTesting various URLs:")
    for url in test_urls:
        detected = detect_instance_type(url)
        print(f"  {url} -> {detected}")


async def async_detection_example():
    """Asynchronous detection example."""
    print("\nAsynchronous Docker/Desktop Detection")
    print("=" * 45)
    
    config = Config.from_env()
    
    # Async detection
    instance_type = await async_detect(config.base_url)
    print(f"Async Detected: {instance_type}")
    
    # Test multiple URLs concurrently
    test_urls = [
        "http://localhost:3001",
        "http://localhost:3000",
        "http://anythingllm:3001"
    ]
    
    print("\nConcurrent URL testing:")
    tasks = [async_detect(url) for url in test_urls]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    for url, result in zip(test_urls, results):
        if isinstance(result, Exception):
            print(f"  {url} -> Error: {result}")
        else:
            print(f"  {url} -> {result}")


def main():
    """Main detection example."""
    print("AnythingLLM Docker/Desktop Detection Example")
    print("=" * 50)
    
    # Run sync example
    sync_detection_example()
    
    # Run async example
    asyncio.run(async_detection_example())
    
    print("\n✓ Detection example completed!")


if __name__ == "__main__":
    main()