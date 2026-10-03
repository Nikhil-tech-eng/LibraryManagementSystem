"""Book Catalog Service — FastAPI application entry point."""
from __future__ import annotations

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from prometheus_fastapi_instrumentator import Instrumentator

from app.database import init_db_pool, close_db_pool, check_db_health
from app.redis_client import init_redis_client, close_redis_client, check_redis_health
from app.routers.books import router as books_router

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown lifecycle management."""
    logger.info("Book Catalog Service starting up…")
    await init_db_pool()
    await init_redis_client()
    logger.info("Database pool and Redis client initialised.")
    yield
    logger.info("Book Catalog Service shutting down…")
    await close_db_pool()
    await close_redis_client()
    logger.info("Connections closed.")


app = FastAPI(
    title="Book Catalog Service",
    description="Manages the LMS book inventory with Redis caching.",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS — allow all origins in dev; tighten in production via env
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Prometheus metrics — exposes /metrics automatically
Instrumentator().instrument(app).expose(app)

# Routers
app.include_router(books_router, prefix="/api")


@app.get("/health", tags=["ops"])
async def health():
    """Liveness probe."""
    return {"status": "UP", "service": "book-catalog"}


@app.get("/ready", tags=["ops"])
async def ready():
    """Readiness probe — checks DB pool and Redis."""
    db_ok = await check_db_health()
    redis_ok = await check_redis_health()
    if db_ok and redis_ok:
        return {"status": "READY", "db": "UP", "redis": "UP"}
    return {
        "status": "NOT_READY",
        "db": "UP" if db_ok else "DOWN",
        "redis": "UP" if redis_ok else "DOWN",
    }, 503
