import os
import asyncpg
from typing import Optional

DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = int(os.getenv("DB_PORT", "5432"))
DB_NAME = os.getenv("DB_NAME", "lms_db")
DB_USER = os.getenv("DB_USER", "lms_user")
DB_PASSWORD = os.getenv("DB_PASSWORD", "lms_password")

pool: Optional[asyncpg.Pool] = None

async def init_db_pool():
    global pool
    try:
        pool = await asyncpg.create_pool(
            host=DB_HOST,
            port=DB_PORT,
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD,
            min_size=2,
            max_size=15,
            command_timeout=10,
        )
        print(f"[book-catalog] Connected to PostgreSQL on {DB_HOST}:{DB_PORT}/{DB_NAME}")
    except Exception as e:
        print(f"[book-catalog] DB Pool Warning: {e}")

async def close_db_pool():
    global pool
    if pool:
        await pool.close()
        print("[book-catalog] PostgreSQL pool closed.")

async def get_db_pool() -> asyncpg.Pool:
    if pool is None:
        raise RuntimeError("DB pool not initialised")
    return pool

async def check_db_health() -> bool:
    if not pool:
        return False
    try:
        async with pool.acquire() as conn:
            val = await conn.fetchval("SELECT 1;")
            return val == 1
    except Exception:
        return False
