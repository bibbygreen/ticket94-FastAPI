import json
import time
from functools import wraps

from fastapi.encoders import jsonable_encoder

from src.logger import logger


def timeit(func):
    """
    Decorator that measures the execution time of a function.
    """

    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        duration = end_time - start_time
        logger.info(f"{func.__name__} took {duration:.4f} seconds.")
        return result

    return wrapper


def redis_cache(expiration: int = 3600):
    """
    Decorator that caches the response of an async function in Redis.

    Args:
        prefix: The prefix for the cache key
        expiration: Cache expiration time in seconds (default: 1 hour)
    """

    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Get redis client from kwargs
            redis_client = kwargs.get("redis_client")

            if not redis_client:
                raise ValueError("Redis client not found in kwargs")

            # Generate cache key based on function arguments
            # Skip self/cls and filter out redis_client/session
            kwarg_values = [
                f"{k}:{v}"
                for k, v in sorted(kwargs.items())
                if k not in ("redis_client", "session")  # Exclude redis and session
            ]
            cache_key = f"{func.__name__}_{str(args)}_{str(kwarg_values)}"

            try:
                # Try to get data from cache
                cached_data = await redis_client.get(cache_key)
                if cached_data:
                    return json.loads(cached_data)

                # If not in cache, execute function
                result = await func(*args, **kwargs)

                # Convert result to JSON-serializable format
                json_result = jsonable_encoder(result)

                # Store result in cache
                await redis_client.set(cache_key, json.dumps(json_result), ex=expiration)

                return result
            except Exception as e:
                logger.error(f"Redis cache error: {str(e)}")
                # If caching fails, just execute the function
                return await func(*args, **kwargs)

        return wrapper

    return decorator
