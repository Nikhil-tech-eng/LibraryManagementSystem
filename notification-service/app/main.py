"""Notification Service — FastAPI application entry point."""
from __future__ import annotations

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from prometheus_fastapi_instrumentator import Instrumentator

from app.database import init_db_pool, close_db_pool, check_db_health
from app.routers.notifications import router as notif_router

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Notification Service starting up…")
    await init_db_pool()
    yield
    logger.info("Notification Service shutting down…")
    await close_db_pool()


app = FastAPI(title="Notification Service", version="1.0.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

Instrumentator().instrument(app).expose(app)
app.include_router(notif_router)


@app.get("/health", tags=["ops"])
async def health():
    return {"status": "UP", "service": "notification-service"}


@app.get("/ready", tags=["ops"])
async def ready():
    db_ok = await check_db_health()
    if db_ok:
        return {"status": "READY", "db": "UP"}
    return {"status": "NOT_READY", "db": "DOWN"}, 503
