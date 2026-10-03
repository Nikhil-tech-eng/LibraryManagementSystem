"""HTTP client with 3-second timeout and 1 retry on 5xx errors."""
from __future__ import annotations

import asyncio
import logging
import os

import httpx

logger = logging.getLogger(__name__)

TIMEOUT = httpx.Timeout(3.0)  # 3-second hard limit per PRD

USER_SERVICE_URL: str = os.getenv("USER_SERVICE_URL", "http://user-service:5002")
BOOK_CATALOG_URL: str = os.getenv("BOOK_CATALOG_URL", "http://book-catalog:5001")
NOTIFICATION_SERVICE_URL: str = os.getenv("NOTIFICATION_SERVICE_URL", "http://notification-service:5004")

_client: httpx.AsyncClient | None = None


async def init_http_client() -> None:
    global _client
    _client = httpx.AsyncClient(timeout=TIMEOUT)
    logger.info("HTTP client initialised.")


async def close_http_client() -> None:
    global _client
    if _client:
        await _client.aclose()
        _client = None


async def _request_with_retry(method: str, url: str, **kwargs) -> httpx.Response:
    """Make an HTTP request; retry once on 5xx after 500 ms."""
    for attempt in range(2):
        resp = await _client.request(method, url, **kwargs)
        if resp.status_code < 500 or attempt == 1:
            return resp
        logger.warning("5xx from %s (attempt %d), retrying…", url, attempt + 1)
        await asyncio.sleep(0.5)
    return resp  # type: ignore[return-value]


async def verify_token(token: str) -> dict:
    resp = await _request_with_retry(
        "GET", f"{USER_SERVICE_URL}/auth/verify",
        headers={"Authorization": f"Bearer {token}"},
    )
    resp.raise_for_status()
    return resp.json()


async def get_book(book_id: int) -> dict:
    resp = await _request_with_retry("GET", f"{BOOK_CATALOG_URL}/api/books/{book_id}")
    resp.raise_for_status()
    return resp.json()


async def patch_book_stock(book_id: int, delta: int) -> dict:
    resp = await _request_with_retry(
        "PATCH", f"{BOOK_CATALOG_URL}/api/books/{book_id}/stock",
        json={"delta": delta},
    )
    resp.raise_for_status()
    return resp.json()


async def notify(payload: dict) -> None:
    """Fire-and-forget notification — errors are logged but NOT raised."""
    try:
        resp = await _request_with_retry(
            "POST", f"{NOTIFICATION_SERVICE_URL}/api/notifications/notify",
            json=payload,
        )
        if resp.status_code >= 400:
            logger.warning("Notification service returned %d: %s", resp.status_code, resp.text)
    except Exception as exc:
        logger.warning("Notification service unreachable (non-fatal): %s", exc)
