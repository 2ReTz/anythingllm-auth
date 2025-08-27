# AnythingLLM Authentication Utilities

Comprehensive Python authentication utilities for AnythingLLM API with support for both Docker and Desktop deployments.

## Features

- Bearer token authentication handling
- Environment-based configuration
- Token validation and refresh utilities
- Docker vs Desktop instance detection
- Synchronous and asynchronous API clients
- Comprehensive error handling
- Configuration templates for different deployment types

## Installation

```bash
pip install -r requirements.txt
```

## Quick Start

```python
from anythingllm_auth import AuthClient

# Initialize client
client = AuthClient()

# Authenticate
token = client.authenticate("username", "password")

# Make authenticated requests
response = client.get("/api/v1/documents")
```

## Project Structure

```
anythingllm-auth/
├── anythingllm_auth/
│   ├── __init__.py
│   ├── auth.py              # Main authentication module
│   ├── config.py            # Configuration management
│   ├── client.py            # API client (sync/async)
│   ├── exceptions.py        # Custom exceptions
│   └── utils.py             # Utility functions
├── examples/
│   ├── basic_auth.py        # Basic authentication example
│   ├── async_example.py     # Async usage example
│   └── docker_detection.py  # Docker vs Desktop detection
├── config/
│   ├── docker.env.template  # Docker deployment config
│   ├── desktop.env.template # Desktop deployment config
│   └── cloud.env.template   # Cloud deployment config
├── tests/
│   └── test_auth.py
├── requirements.txt
└── README.md