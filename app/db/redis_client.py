"""
Redis Client Setup
Handles Redis connection for caching and real-time features
"""
import redis
from app.core.config import settings

# Create Redis client
redis_client = redis.from_url(
    settings.REDIS_URL,
    decode_responses=True,  # Automatically decode bytes to strings
    socket_connect_timeout=5,
    socket_timeout=5
)

def get_redis():
    """Get Redis client instance"""
    return redis_client

def ping_redis():
    """Check if Redis is connected"""
    try:
        return redis_client.ping()
    except Exception as e:
        print(f"Redis connection error: {e}")
        return False

# Helper functions for common operations
def cache_set(key: str, value: str, expire: int = 3600):
    """Set a value in Redis cache with expiration"""
    try:
        redis_client.setex(key, expire, value)
        return True
    except Exception as e:
        print(f"Cache set error: {e}")
        return False

def cache_get(key: str):
    """Get a value from Redis cache"""
    try:
        return redis_client.get(key)
    except Exception as e:
        print(f"Cache get error: {e}")
        return None

def cache_delete(key: str):
    """Delete a key from Redis cache"""
    try:
        redis_client.delete(key)
        return True
    except Exception as e:
        print(f"Cache delete error: {e}")
        return False