# agentswarm-redis-store

Redis implementation of the `Store` interface for [ai-agentswarm](https://github.com/ai-agentswarm/agentswarm).

## Security Configuration

This project focuses on secure Redis connections. It supports:
- **SSL/TLS**: For encrypted communication.
- **ACL/Passwords**: For authenticated access.
- **Safe Serialization**: Uses JSON by default for structured data.

## Installation

```bash
# Clone the repository
cd agentswarm-redis-store

# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -e .
```

## Security Focus

The `RedisStore` is designed with security as a primary concern:
- **SSL/TLS**: Mandatory for production environments to prevent eavesdropping.
- **Authentication**: Supports both legacy `password` and modern Redis 6+ `username`/`password` ACLs.
- **Secure Reconstruction**: `to_dict()` returns a minimal configuration that triggers reconstruction from environment variables on the remote side, ensuring sensitive credentials are never serialized or transmitted.
- **Client Injection**: Allows passing a pre-configured `redis.Redis` client for advanced use cases (e.g., custom pooling, sentinel).

## Configuration Environment Variables

When using `RedisStore.from_env()` or remote reconstruction, the following environment variables are supported:

| Variable | Description | Default |
|----------|-------------|---------|
| `REDIS_HOST` | Redis server hostname | `localhost` |
| `REDIS_PORT` | Redis server port | `6379` |
| `REDIS_DB`   | Redis database number | `0` |
| `REDIS_USERNAME` | Username for ACL authentication | `None` |
| `REDIS_PASSWORD` | Password for authentication | `None` |
| `REDIS_SSL` | Enable SSL/TLS connection (`true`/`false`) | `false` |

## Usage

### Environmental Configuration (Recommended)
Set `REDIS_HOST`, `REDIS_PASSWORD`, etc., in your environment and use:
```python
from agentswarm.redis.store import RedisStore
store = RedisStore.from_env()
```

### Direct Client Injection
```python
import redis
from agentswarm.redis.store import RedisStore

client = redis.Redis(host="localhost", db=0)
store = RedisStore(redis_client=client)
```

### Remote Reconstruction
```python
store = RedisStore.from_env()
config = store.to_dict() # Returns {"recreate_from_env": True}

# On a remote machine (with its own REDIS_HOST env var)
remote_store = RedisStore.recreate(config)
```
