import os
import redis

SESSION_STORE = os.getenv("SESSION_STORE", "database")
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")

# Initialize Redis client if needed
redis_client = None
if SESSION_STORE == "redis":
    try:
        redis_client = redis.from_url(REDIS_URL, decode_responses=True)
        # Test connection
        redis_client.ping()
        print("Redis session storage enabled.")
    except Exception as e:
        print(f"Failed to connect to Redis: {e}. Falling back to database session storage.")
        SESSION_STORE = "database"
        redis_client = None

def get_user_id_from_cache(token: str):
    """
    Get user_id from Redis cache using session token.
    """
    if SESSION_STORE == "redis" and redis_client and token:
        return redis_client.get(f"session:{token}")
    return None

def set_user_id_to_cache(token: str, user_id: str, ttl: int = 60 * 60 * 24 * 30):
    """
    Cache token -> user_id mapping in Redis.
    """
    if SESSION_STORE == "redis" and redis_client and token and user_id:
        redis_client.setex(f"session:{token}", ttl, user_id)

def remove_token_from_cache(token: str):
    """
    Remove token from Redis cache.
    """
    if SESSION_STORE == "redis" and redis_client and token:
        redis_client.delete(f"session:{token}")
