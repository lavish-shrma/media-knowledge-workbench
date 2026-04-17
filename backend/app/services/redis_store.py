from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from datetime import timedelta
import json
from typing import Any

from app.core.config import get_settings

try:
    import redis
except Exception:  # pragma: no cover - fallback for environments without redis installed
    redis = None


@dataclass
class _MemoryEntry:
    value: str
    expires_at: datetime | None = None


@dataclass
class _MemoryStore:
    values: dict[str, _MemoryEntry] = field(default_factory=dict)
    counters: dict[str, int] = field(default_factory=dict)

    def _is_expired(self, entry: _MemoryEntry) -> bool:
        return entry.expires_at is not None and datetime.now(timezone.utc) >= entry.expires_at

    def get(self, key: str) -> str | None:
        entry = self.values.get(key)
        if entry is None:
            return None
        if self._is_expired(entry):
            self.values.pop(key, None)
            return None
        return entry.value

    def setex(self, key: str, ttl_seconds: int, value: str) -> None:
        self.values[key] = _MemoryEntry(
            value=value,
            expires_at=datetime.now(timezone.utc) + timedelta(seconds=ttl_seconds),
        )

    def incr(self, key: str) -> int:
        self.counters[key] = self.counters.get(key, 0) + 1
        return self.counters[key]

    def expire(self, key: str, ttl_seconds: int) -> None:
        entry = self.values.get(key)
        if entry is not None:
            entry.expires_at = datetime.now(timezone.utc) + timedelta(seconds=ttl_seconds)

    def delete(self, key: str) -> None:
        self.values.pop(key, None)
        self.counters.pop(key, None)


_memory_store = _MemoryStore()
_redis_client = None


def _get_redis_client():
    global _redis_client
    if _redis_client is not None:
        return _redis_client

    settings = get_settings()
    if redis is None:
        _redis_client = _memory_store
        return _redis_client

    try:
        _redis_client = redis.Redis.from_url(settings.redis_url, decode_responses=True)
        _redis_client.ping()
    except Exception:
        _redis_client = _memory_store
    return _redis_client


def cache_get_json(key: str) -> Any | None:
    client = _get_redis_client()
    raw = client.get(key)
    if raw is None:
        return None
    if isinstance(raw, bytes):
        raw = raw.decode("utf-8")
    return json.loads(raw)


def cache_set_json(key: str, value: Any, ttl_seconds: int) -> None:
    client = _get_redis_client()
    encoded = json.dumps(value)
    if hasattr(client, "setex"):
        client.setex(key, ttl_seconds, encoded)
    else:
        client.setex(key, ttl_seconds, encoded)


def cache_has_key(key: str) -> bool:
    client = _get_redis_client()
    return client.get(key) is not None


def increment_rate_limit(key: str, ttl_seconds: int = 60) -> int:
    client = _get_redis_client()
    if hasattr(client, "incr"):
        current = int(client.incr(key))
        if current == 1 and hasattr(client, "expire"):
            client.expire(key, ttl_seconds)
        return current

    current = _memory_store.incr(key)
    if current == 1:
        _memory_store.expire(key, ttl_seconds)
    return current


def rate_limit_key(scope: str, actor: str) -> str:
    return f"rate-limit:{scope}:{actor}"


def cache_key(scope: str, signature: str) -> str:
    return f"cache:{scope}:{signature}"


def reset_store() -> None:
    if _redis_client is _memory_store or _redis_client is None:
        _memory_store.values.clear()
        _memory_store.counters.clear()
