"""
Redis cache for scraping operations
"""
import json
from typing import Optional, Any
import redis
from loguru import logger


class Cache:
    """Redis cache manager"""

    def __init__(self, redis_url: str):
        try:
            self.client = redis.from_url(
                redis_url,
                decode_responses=True,
                socket_timeout=5
            )
            self.client.ping()
            logger.info("Redis cache connected")
        except Exception as e:
            logger.error(f"Failed to connect to Redis: {e}")
            self.client = None

    def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        if not self.client:
            return None

        try:
            value = self.client.get(key)
            if value:
                return json.loads(value)
            return None
        except Exception as e:
            logger.error(f"Cache get error: {e}")
            return None

    def set(self, key: str, value: Any, ttl: int = 3600) -> bool:
        """
        Set value in cache

        Args:
            key: Cache key
            value: Value to cache
            ttl: Time to live in seconds (default 1 hour)

        Returns:
            True if successful
        """
        if not self.client:
            return False

        try:
            serialized = json.dumps(value)
            self.client.setex(key, ttl, serialized)
            return True
        except Exception as e:
            logger.error(f"Cache set error: {e}")
            return False

    def delete(self, key: str) -> bool:
        """Delete key from cache"""
        if not self.client:
            return False

        try:
            self.client.delete(key)
            return True
        except Exception as e:
            logger.error(f"Cache delete error: {e}")
            return False

    def exists(self, key: str) -> bool:
        """Check if key exists"""
        if not self.client:
            return False

        try:
            return self.client.exists(key) > 0
        except Exception as e:
            logger.error(f"Cache exists error: {e}")
            return False

    def get_stats(self) -> dict:
        """Get cache statistics"""
        if not self.client:
            return {}

        try:
            info = self.client.info('stats')
            return {
                'total_commands': info.get('total_commands_processed', 0),
                'hits': info.get('keyspace_hits', 0),
                'misses': info.get('keyspace_misses', 0),
                'keys': self.client.dbsize()
            }
        except Exception as e:
            logger.error(f"Error getting cache stats: {e}")
            return {}

    def clear_pattern(self, pattern: str) -> int:
        """Clear all keys matching pattern"""
        if not self.client:
            return 0

        try:
            keys = self.client.keys(pattern)
            if keys:
                return self.client.delete(*keys)
            return 0
        except Exception as e:
            logger.error(f"Error clearing pattern {pattern}: {e}")
            return 0

    def increment(self, key: str, amount: int = 1) -> Optional[int]:
        """Increment counter"""
        if not self.client:
            return None

        try:
            return self.client.incrby(key, amount)
        except Exception as e:
            logger.error(f"Cache increment error: {e}")
            return None
