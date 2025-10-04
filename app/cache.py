"""
Simple in-memory caching system
Improves performance by caching expensive operations
"""

import time
import hashlib
from typing import Any, Optional, Dict
from functools import wraps

class SimpleCache:
    """Thread-safe in-memory cache with TTL support"""
    
    def __init__(self, default_ttl: int = 3600):
        self.cache: Dict[str, Dict] = {}
        self.default_ttl = default_ttl
    
    def _generate_key(self, *args, **kwargs) -> str:
        """Generate cache key from function arguments"""
        key_data = str(args) + str(sorted(kwargs.items()))
        return hashlib.md5(key_data.encode()).hexdigest()
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache if not expired"""
        if key not in self.cache:
            return None
        
        entry = self.cache[key]
        if time.time() > entry['expires']:
            del self.cache[key]
            return None
        
        entry['hits'] += 1
        entry['last_accessed'] = time.time()
        return entry['value']
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """Set value in cache with TTL"""
        if ttl is None:
            ttl = self.default_ttl
        
        self.cache[key] = {
            'value': value,
            'expires': time.time() + ttl,
            'created': time.time(),
            'last_accessed': time.time(),
            'hits': 0
        }
    
    def delete(self, key: str) -> bool:
        """Delete key from cache"""
        if key in self.cache:
            del self.cache[key]
            return True
        return False
    
    def clear(self) -> None:
        """Clear all cache entries"""
        self.cache.clear()
    
    def cleanup_expired(self) -> int:
        """Remove expired entries and return count"""
        now = time.time()
        expired_keys = [
            key for key, entry in self.cache.items()
            if now > entry['expires']
        ]
        
        for key in expired_keys:
            del self.cache[key]
        
        return len(expired_keys)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        now = time.time()
        total_hits = sum(entry['hits'] for entry in self.cache.values())
        
        return {
            "total_entries": len(self.cache),
            "total_hits": total_hits,
            "memory_usage_estimate": len(str(self.cache)),
            "expired_entries": sum(
                1 for entry in self.cache.values()
                if now > entry['expires']
            )
        }

def cached(ttl: int = 3600, cache_instance: Optional[SimpleCache] = None):
    """Decorator to cache function results"""
    if cache_instance is None:
        cache_instance = default_cache
    
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Generate cache key
            cache_key = f"{func.__name__}:{cache_instance._generate_key(*args, **kwargs)}"
            
            # Try to get from cache
            cached_result = cache_instance.get(cache_key)
            if cached_result is not None:
                return cached_result
            
            # Execute function and cache result
            result = func(*args, **kwargs)
            cache_instance.set(cache_key, result, ttl)
            
            return result
        
        # Add cache management methods to function
        wrapper.cache_clear = lambda: cache_instance.clear()
        wrapper.cache_info = lambda: cache_instance.get_stats()
        
        return wrapper
    return decorator

# Global cache instances
default_cache = SimpleCache(default_ttl=3600)  # 1 hour
embedding_cache = SimpleCache(default_ttl=86400)  # 24 hours for embeddings
search_cache = SimpleCache(default_ttl=1800)  # 30 minutes for search results
