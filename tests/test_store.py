import pytest
import fakeredis
from agentswarm.redis.store import RedisStore


@pytest.fixture
def mock_redis_store():
    store = RedisStore(host="localhost", port=6379)
    # Patch the internal client with fakeredis
    store._client = fakeredis.FakeRedis(decode_responses=True)
    return store


def test_set_get(mock_redis_store):
    mock_redis_store.set("test_key", {"a": 1, "b": "test"})
    assert mock_redis_store.get("test_key") == {"a": 1, "b": "test"}


def test_has(mock_redis_store):
    mock_redis_store.set("test_key", "value")
    assert mock_redis_store.has("test_key") is True
    assert mock_redis_store.has("missing_key") is False


def test_items(mock_redis_store):
    mock_redis_store.set("k1", "v1")
    mock_redis_store.set("k2", {"deep": "value"})
    items = mock_redis_store.items()
    assert items == {"k1": "v1", "k2": {"deep": "value"}}


def test_client_injection():
    mock_client = fakeredis.FakeRedis(decode_responses=True)
    store = RedisStore(redis_client=mock_client)
    assert store._client == mock_client
    store.set("test", 123)
    assert mock_client.get("test") == "123"


def test_to_dict_recreate_env(monkeypatch):
    monkeypatch.setenv("REDIS_HOST", "env-host")
    store = RedisStore(host="manual-host")
    config = store.to_dict()
    assert config == {"recreate_from_env": True}

    new_store = RedisStore.recreate(config)
    assert new_store._config["host"] == "env-host"


def test_from_env(monkeypatch):
    monkeypatch.setenv("REDIS_HOST", "env-host")
    monkeypatch.setenv("REDIS_PORT", "9999")
    store = RedisStore.from_env(db=5)
    assert store._config["host"] == "env-host"
    assert store._config["port"] == 9999
    assert store._config["db"] == 5


def test_recreate_no_env():
    config = {"host": "remote-host", "port": 1234, "db": 1, "ssl": True}
    store = RedisStore.recreate(config)
    assert store._config["host"] == "remote-host"
    assert store._config["port"] == 1234
    assert store._config["db"] == 1
    assert store._config["ssl"] is True
