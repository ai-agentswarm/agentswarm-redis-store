import json
import logging
from typing import Any, Optional
import redis
from pydantic import PrivateAttr
from agentswarm.datamodels.store import Store

logger = logging.getLogger(__name__)


class RedisStore(Store):
    """
    Redis implementation of the Store interface.
    Focuses on security and robustness.
    """

    _client: redis.Redis = PrivateAttr()
    _config: dict = PrivateAttr()

    def __init__(
        self,
        redis_client: Optional[redis.Redis] = None,
        host: str = "localhost",
        port: int = 6379,
        db: int = 0,
        username: Optional[str] = None,
        password: Optional[str] = None,
        ssl: bool = False,
        ssl_cert_reqs: str = "required",
        decode_responses: bool = True,
        **kwargs,
    ):
        """
        Initialize the Redis store.
        If redis_client is provided, it is used directly.
        Otherwise, a new client is created using the provided config.
        """
        self._config = {
            "host": host,
            "port": port,
            "db": db,
            "username": username,
            "password": password,
            "ssl": ssl,
            "ssl_cert_reqs": ssl_cert_reqs,
            "decode_responses": decode_responses,
            **kwargs,
        }

        if redis_client:
            self._client = redis_client
        else:
            self._client = redis.Redis(**self._config)

    @classmethod
    def from_env(cls, **overrides) -> "RedisStore":
        """
        Factory method to create a RedisStore from environment variables.
        Useful for secure configuration without passing secrets in dicts.
        """
        import os

        config = {
            "host": os.getenv("REDIS_HOST", "localhost"),
            "port": int(os.getenv("REDIS_PORT", 6379)),
            "db": int(os.getenv("REDIS_DB", 0)),
            "username": os.getenv("REDIS_USERNAME"),
            "password": os.getenv("REDIS_PASSWORD"),
            "ssl": os.getenv("REDIS_SSL", "false").lower() == "true",
            "decode_responses": True,
        }
        config.update(overrides)
        return cls(**config)

    def get(self, key: str) -> Any:
        """
        Obtains the value associated with the given key.
        Deserializes JSON content if possible.
        """
        value = self._client.get(key)
        if value is None:
            return None
        try:
            return json.loads(value)
        except (json.JSONDecodeError, TypeError):
            return value

    def set(self, key: str, value: Any):
        """
        Sets the value associated with the given key.
        Serializes JSON content.
        """
        serialized_value = json.dumps(value)
        self._client.set(key, serialized_value)

    def has(self, key: str) -> bool:
        """
        Checks if the store has a value associated with the given key.
        """
        return self._client.exists(key) > 0

    def items(self) -> dict[str, Any]:
        """
        Returns all key-value pairs in the store.
        """
        result = {}
        for key in self._client.scan_iter("*"):
            result[key] = self.get(key)
        return result

    def to_dict(self) -> dict:
        """
        Returns a minimal configuration needed to recreate the store.
        Avoids sharing sensitive information like passwords.
        """
        # Return a trigger for environmental reconstruction
        return {"recreate_from_env": True}

    @classmethod
    def recreate(cls, config: dict) -> "RedisStore":
        """
        Recreates a RedisStore instance.
        If 'recreate_from_env' is present, it uses environment variables.
        """
        if config.get("recreate_from_env"):
            return cls.from_env()
        return cls(**config)
