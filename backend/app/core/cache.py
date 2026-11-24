import json
import logging
import time
from typing import Any, Optional
import redis

from backend.app.core.config import settings

logger = logging.getLogger(__name__)


class InMemoryCache:
    """In-memory cache fallback with TTL support when Redis is unreachable."""
    def __init__(self):
        self._store = {}
        self._expiry = {}

    def get(self, key: str) -> Optional[str]:
        now = time.time()
        if key in self._expiry and self._expiry[key] < now:
            self.delete(key)
            return None
        return self._store.get(key)

    def set(self, key: str, value: str, ex: Optional[int] = None) -> bool:
        self._store[key] = value
        if ex:
            self._expiry[key] = time.time() + ex
        elif key in self._expiry:
            del self._expiry[key]
        return True

    def delete(self, key: str) -> bool:
        existed = key in self._store
        self._store.pop(key, None)
        self._expiry.pop(key, None)
        return existed

    def delete_pattern(self, pattern: str) -> int:
        prefix = pattern.replace("*", "")
        keys_to_del = [k for k in self._store if k.startswith(prefix)]
        count = 0
        for k in keys_to_del:
            if self.delete(k):
                count += 1
        return count

    def clear(self):
        self._store.clear()
        self._expiry.clear()


class CacheService:
    def __init__(self):
        self._redis: Optional[redis.Redis] = None
        self._memory = InMemoryCache()
        self._connected = False
        self._init_redis()

    def _init_redis(self):
        if not settings.CACHE_ENABLED or settings.ENVIRONMENT == "testing":
            self._connected = False
            return
        try:
            r = redis.from_url(
                settings.REDIS_URL,
                decode_responses=True,
                socket_timeout=0.1,
                socket_connect_timeout=0.1,
            )
            r.ping()
            self._redis = r
            self._connected = True
            logger.info("Connected to Redis cache successfully.")
        except Exception as e:
            logger.warning("Redis connection failed (%s); using in-memory cache fallback.", e)
            self._redis = None
            self._connected = False

    @property
    def is_redis_connected(self) -> bool:
        if self._redis:
            try:
                return bool(self._redis.ping())
            except Exception:
                return False
        return False

    def get(self, key: str) -> Optional[Any]:
        if not settings.CACHE_ENABLED:
            return None
        try:
            if self.is_redis_connected:
                raw = self._redis.get(key)
            else:
                raw = self._memory.get(key)

            if raw is not None:
                return json.loads(raw)
        except Exception as e:
            logger.error("Error reading from cache key '%s': %s", key, e)
        return None

    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        if not settings.CACHE_ENABLED:
            return False
        ttl_seconds = ttl if ttl is not None else settings.CACHE_DEFAULT_TTL
        try:
            serialized = json.dumps(value, default=str)
            if self.is_redis_connected:
                return bool(self._redis.set(key, serialized, ex=ttl_seconds))
            else:
                return self._memory.set(key, serialized, ex=ttl_seconds)
        except Exception as e:
            logger.error("Error writing to cache key '%s': %s", key, e)
            return False

    def delete(self, key: str) -> bool:
        try:
            if self.is_redis_connected:
                return bool(self._redis.delete(key))
            else:
                return self._memory.delete(key)
        except Exception as e:
            logger.error("Error deleting cache key '%s': %s", key, e)
            return False

    def delete_pattern(self, pattern: str) -> int:
        count = 0
        try:
            if self.is_redis_connected:
                keys = self._redis.keys(pattern)
                if keys:
                    count = self._redis.delete(*keys)
            else:
                count = self._memory.delete_pattern(pattern)
        except Exception as e:
            logger.error("Error deleting pattern '%s': %s", pattern, e)
        return count

    def invalidate_user_cache(self, user_id: int) -> int:
        """Invalidate all cached reports and summaries for a specific user."""
        pattern = f"user:{user_id}:*"
        count = self.delete_pattern(pattern)
        logger.info("Invalidated %d cache keys matching '%s'", count, pattern)
        return count

    def clear(self):
        """Clear all keys in cache."""
        try:
            if self.is_redis_connected:
                self._redis.flushdb()
            else:
                self._memory.clear()
        except Exception:
            self._memory.clear()


cache = CacheService()
