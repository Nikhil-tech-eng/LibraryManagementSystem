"""User Service — FastAPI application entry point."""
from __future__ import annotations

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from prometheus_fastapi_instrumentator import Instrumentator

from app.database import init_db_pool, close_db_pool, check_db_health
from app.redis_client import init_redis_client, close_redis_client, check_redis_health
from app.routers.users import router as users_router

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("User Service starting up…")
    await init_db_pool()
    await init_redis_client()
    yield
    logger.info("User Service shutting down…")
    await close_db_pool()
    await close_redis_client()


app = FastAPI(title="User & Auth Service", version="1.0.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

Instrumentator().instrument(app).expose(app)
app.include_router(users_router)


@app.get("/health", tags=["ops"])
async def health():
    return {"status": "UP", "service": "user-service"}


@app.get("/ready", tags=["ops"])
async def ready():
    db_ok = await check_db_health()
    redis_ok = await check_redis_health()
    if db_ok and redis_ok:
        return {"status": "READY", "db": "UP", "redis": "UP"}
    return {"status": "NOT_READY", "db": "UP" if db_ok else "DOWN", "redis": "UP" if redis_ok else "DOWN"}, 503
