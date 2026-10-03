"""User-service Redis client — session blacklist helpers."""
from __future__ import annotations

import logging
import os

import redis.asyncio as aioredis

logger = logging.getLogger(__name__)

_redis: aioredis.Redis | None = None


async def init_redis_client() -> None:
    global _redis
    _redis = aioredis.from_url(
        f"redis://{os.getenv('REDIS_HOST', 'localhost')}:{os.getenv('REDIS_PORT', '6379')}",
        decode_responses=True,
    )
    logger.info("Redis client initialised (user-service).")


async def close_redis_client() -> None:
    global _redis
    if _redis:
        await _redis.aclose()
        _redis = None


async def get_redis_client() -> aioredis.Redis:
    if _redis is None:
        raise RuntimeError("Redis client not initialised")
    return _redis


async def check_redis_health() -> bool:
    try:
        return await _redis.ping()
    except Exception as exc:
        logger.error("Redis health check failed: %s", exc)
        return False


async def blacklist_token(jti: str, exp_seconds: int) -> None:
    """Add a JWT ID to the blacklist until it would naturally expire."""
    key = f"session:blacklist:{jti}"
    await _redis.setex(key, exp_seconds, "1")


async def is_token_blacklisted(jti: str) -> bool:
    key = f"session:blacklist:{jti}"
    return await _redis.exists(key) == 1
