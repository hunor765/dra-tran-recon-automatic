"""Caching utilities for API responses and expensive operations.

Provides Redis-based caching with fallback to in-memory for development.
"""
import functools
import hashlib
import json
import logging
import pickle
from typing import Any, Callable, Optional, Union

from core.config import settings

logger = logging.getLogger(__name__)

# Try to import redis, fallback to memory if not available
try:
    import redis.asyncio as redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False
    logger.warning("Redis not installed, using in-memory cache")


class CacheBackend:
    """Abstract cache backend interface."""
    
    async def get(self, key: str) -> Optional[Any]:
        raise NotImplementedError
    
    async def set(
        self,
        key: str,
        value: Any,
        ttl: Optional[int] = None
    ) -> None:
        raise NotImplementedError
    
    async def delete(self, key: str) -> None:
        raise NotImplementedError
    
    async def clear(self) -> None:
        raise NotImplementedError


class MemoryCache(CacheBackend):
    """In-memory cache backend for development.
    
    Note: This is not suitable for production with multiple workers.
    """
    
    def __init__(self):
        self._cache: dict[str, tuple[Any, Optional[float]]] = {}
        self._logger = logging.getLogger(f"{__name__}.MemoryCache")
    
    async def get(self, key: str) -> Optional[Any]:
        import time
        
        if key not in self._cache:
            return None
        
        value, expiry = self._cache[key]
        
        # Check if expired
        if expiry is not None and time.time() > expiry:
            del self._cache[key]
            return None
        
        self._logger.debug(f"Cache hit: {key}")
        return value
    
    async def set(
        self,
        key: str,
        value: Any,
        ttl: Optional[int] = None
    ) -> None:
        import time
        
        expiry = time.time() + ttl if ttl else None
        self._cache[key] = (value, expiry)
        self._logger.debug(f"Cache set: {key} (ttl={ttl}s)")
    
    async def delete(self, key: str) -> None:
        if key in self._cache:
            del self._cache[key]
            self._logger.debug(f"Cache delete: {key}")
    
    async def clear(self) -> None:
        self._cache.clear()
        self._logger.info("Cache cleared")


class RedisCache(CacheBackend):
    """Redis cache backend for production."""
    
    def __init__(self, redis_url: str):
        self._redis = redis.from_url(redis_url, decode_responses=False)
        self._logger = logging.getLogger(f"{__name__}.RedisCache")
    
    async def get(self, key: str) -> Optional[Any]:
        try:
            data = await self._redis.get(key)
            if data is None:
                return None
            
            value = pickle.loads(data)
            self._logger.debug(f"Cache hit: {key}")
            return value
        except Exception as e:
            self._logger.error(f"Cache get error: {e}")
            return None
    
    async def set(
        self,
        key: str,
        value: Any,
        ttl: Optional[int] = None
    ) -> None:
        try:
            data = pickle.dumps(value)
            if ttl:
                await self._redis.setex(key, ttl, data)
            else:
                await self._redis.set(key, data)
            self._logger.debug(f"Cache set: {key} (ttl={ttl}s)")
        except Exception as e:
            self._logger.error(f"Cache set error: {e}")
    
    async def delete(self, key: str) -> None:
        try:
            await self._redis.delete(key)
            self._logger.debug(f"Cache delete: {key}")
        except Exception as e:
            self._logger.error(f"Cache delete error: {e}")
    
    async def clear(self) -> None:
        try:
            await self._redis.flushdb()
            self._logger.info("Cache cleared")
        except Exception as e:
            self._logger.error(f"Cache clear error: {e}")


# Global cache instance
_cache_instance: Optional[CacheBackend] = None


def get_cache() -> CacheBackend:
    """Get or create the global cache instance.
    
    Returns:
        CacheBackend: Redis cache if REDIS_URL is set, otherwise memory cache
    """
    global _cache_instance
    
    if _cache_instance is not None:
        return _cache_instance
    
    if not settings.CACHE_ENABLED:
        logger.info("Caching is disabled")
        _cache_instance = MemoryCache()  # Still use memory cache but won't be used
        return _cache_instance
    
    if settings.REDIS_URL and REDIS_AVAILABLE:
        logger.info(f"Using Redis cache: {settings.REDIS_URL}")
        _cache_instance = RedisCache(settings.REDIS_URL)
    else:
        if settings.REDIS_URL and not REDIS_AVAILABLE:
            logger.warning("REDIS_URL set but redis not installed, using memory cache")
        else:
            logger.info("Using in-memory cache")
        _cache_instance = MemoryCache()
    
    return _cache_instance


def generate_cache_key(*args: Any, **kwargs: Any) -> str:
    """Generate a cache key from function arguments.
    
    Args:
        *args: Positional arguments
        **kwargs: Keyword arguments
        
    Returns:
        str: MD5 hash of serialized arguments
    """
    # Create a stable string representation
    key_data = json.dumps({
        "args": args,
        "kwargs": sorted(kwargs.items())  # Sort for consistency
    }, sort_keys=True, default=str)
    
    return hashlib.md5(key_data.encode()).hexdigest()


def cached(
    ttl: Optional[int] = None,
    key_prefix: str = "",
    skip_args: Optional[list[int]] = None
) -> Callable:
    """Decorator to cache function results.
    
    Args:
        ttl: Time to live in seconds (default: CACHE_TTL_SECONDS from settings)
        key_prefix: Prefix for cache key
        skip_args: Argument indices to exclude from cache key (e.g., [0] to skip self)
        
    Example:
        @cached(ttl=600, key_prefix="ga4")
        async def fetch_data(self, days: int = 30) -> pd.DataFrame:
            ...
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def async_wrapper(*args: Any, **kwargs: Any) -> Any:
            if not settings.CACHE_ENABLED:
                return await func(*args, **kwargs)
            
            cache = get_cache()
            
            # Filter out skipped arguments
            cache_args = args
            if skip_args:
                cache_args = tuple(
                    arg for i, arg in enumerate(args) if i not in skip_args
                )
            
            # Generate cache key
            key_suffix = generate_cache_key(*cache_args, **kwargs)
            cache_key = f"{key_prefix}:{func.__name__}:{key_suffix}" if key_prefix else f"{func.__name__}:{key_suffix}"
            
            # Try to get from cache
            cached_value = await cache.get(cache_key)
            if cached_value is not None:
                logger.debug(f"Cache hit for {func.__name__}")
                return cached_value
            
            # Call function and cache result
            result = await func(*args, **kwargs)
            
            cache_ttl = ttl or settings.CACHE_TTL_SECONDS
            await cache.set(cache_key, result, cache_ttl)
            
            return result
        
        # Attach cache management methods to the function
        async_wrapper.cache_clear = lambda: get_cache().clear()
        async_wrapper.cache_delete = lambda *a, **kw: get_cache().delete(
            f"{key_prefix}:{func.__name__}:{generate_cache_key(*a, **kw)}" if key_prefix 
            else f"{func.__name__}:{generate_cache_key(*a, **kw)}"
        )
        
        return async_wrapper
    
    return decorator


class CacheInvalidator:
    """Helper for invalidating cache entries by pattern."""
    
    def __init__(self, cache: CacheBackend):
        self._cache = cache
        self._logger = logging.getLogger(f"{__name__}.CacheInvalidator")
    
    async def invalidate_client(self, client_id: int) -> None:
        """Invalidate all cache entries for a client.
        
        Call this when connectors are updated for a client.
        """
        # For Redis, we could use SCAN with pattern matching
        # For now, this is a placeholder for more sophisticated invalidation
        self._logger.info(f"Invalidating cache for client {client_id}")
    
    async def invalidate_connector(self, connector_id: int) -> None:
        """Invalidate cache entries for a specific connector."""
        self._logger.info(f"Invalidating cache for connector {connector_id}")


def get_cache_invalidator() -> CacheInvalidator:
    """Get a cache invalidator instance."""
    return CacheInvalidator(get_cache())
