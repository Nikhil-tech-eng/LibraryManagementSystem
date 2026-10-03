"""Book-catalog Redis client — cache-aside pattern."""
from __future__ import annotations

import logging
import os
from typing import Optional

import redis.asyncio as aioredis

logger = logging.getLogger(__name__)

_redis: Optional[aioredis.Redis] = None


async def init_redis_client() -> None:
    global _redis
    host = os.getenv("REDIS_HOST", "localhost")
    port = int(os.getenv("REDIS_PORT", "6379"))
    password = os.getenv("REDIS_PASSWORD", None)
    _redis = aioredis.from_url(
        f"redis://{host}:{port}",
        password=password,
        decode_responses=True,
    )
    try:
        await _redis.ping()
        logger.info(f"Connected to Redis on {host}:{port}")
    except Exception as e:
        logger.warning(f"Redis connection warning: {e}")


async def close_redis_client() -> None:
    global _redis
    if _redis:
        await _redis.aclose()
        _redis = None
        logger.info("Redis connection closed.")


async def get_redis_client() -> aioredis.Redis:
    if _redis is None:
        raise RuntimeError("Redis client not initialised")
    return _redis


async def check_redis_health() -> bool:
    if not _redis:
        return False
    try:
        return await _redis.ping()
    except Exception as exc:
        logger.error(f"Redis health check failed: {exc}")
        return False


async def get_cached(redis_instance: aioredis.Redis, key: str) -> Optional[str]:
    try:
        return await redis_instance.get(key)
    except Exception as exc:
        logger.warning(f"Redis get failed for {key}: {exc}")
        return None


async def set_cached(redis_instance: aioredis.Redis, key: str, value: str, ttl: int = 60) -> None:
    try:
        await redis_instance.setex(key, ttl, value)
    except Exception as exc:
        logger.warning(f"Redis set failed for {key}: {exc}")


async def invalidate_cache(redis_instance: aioredis.Redis, key: str) -> None:
    try:
        await redis_instance.delete(key)
    except Exception as exc:
        logger.warning(f"Redis delete failed for {key}: {exc}")
