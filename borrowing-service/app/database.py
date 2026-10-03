"""Borrowing-service DB pool — asyncpg."""
from __future__ import annotations

import logging
import os

import asyncpg

logger = logging.getLogger(__name__)

_pool: asyncpg.Pool | None = None


async def init_db_pool() -> None:
    global _pool
    _pool = await asyncpg.create_pool(
        host=os.getenv("DB_HOST", "localhost"),
        port=int(os.getenv("DB_PORT", "5432")),
        database=os.getenv("DB_NAME", "lms_db"),
        user=os.getenv("DB_USER", "lms_user"),
        password=os.getenv("DB_PASSWORD", "lms_password"),
        min_size=2,
        max_size=10,
    )
    logger.info("DB pool initialised (borrowing-service).")


async def close_db_pool() -> None:
    global _pool
    if _pool:
        await _pool.close()
        _pool = None


async def get_db_pool() -> asyncpg.Pool:
    if _pool is None:
        raise RuntimeError("DB pool not initialised")
    return _pool


async def check_db_health() -> bool:
    try:
        async with _pool.acquire() as conn:
            await conn.fetchval("SELECT 1")
        return True
    except Exception as exc:
        logger.error("DB health check failed: %s", exc)
        return False
