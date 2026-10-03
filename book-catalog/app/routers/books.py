"""Book Catalog router — CRUD + stock management with Redis cache-aside."""
from __future__ import annotations

import json
import logging
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import JSONResponse

from app.database import get_db_pool
from app.models import BookCreate, BookResponse, BookStockDelta, BookUpdate
from app.redis_client import get_redis_client, get_cached, set_cached, invalidate_cache
from app.auth import require_staff

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/books", tags=["books"])

CACHE_LIST_KEY = "cache:books:list"
CACHE_ITEM_KEY = "cache:books:{book_id}"
CACHE_LIST_TTL = 60      # seconds
CACHE_ITEM_TTL = 120     # seconds


def _item_key(book_id: int) -> str:
    return CACHE_ITEM_KEY.format(book_id=book_id)


async def _fetch_book_by_id(pool, book_id: int) -> dict | None:
    """Query a single book row from the DB."""
    async with pool.acquire() as conn:
        row = await conn.fetchrow(
            "SELECT * FROM books WHERE id = $1", book_id
        )
    return dict(row) if row else None


@router.get("", response_model=list[BookResponse])
async def list_books(
    genre: Optional[str] = Query(None, description="Filter by genre"),
    search: Optional[str] = Query(None, description="Keyword search in title/author"),
    available: Optional[bool] = Query(None, description="Only show books with stock > 0"),
    pool=Depends(get_db_pool),
    redis=Depends(get_redis_client),
):
    """Return all books with optional filters. Results are cached for 60 s when no filters."""
    use_cache = genre is None and search is None and available is None

    if use_cache:
        cached = await get_cached(redis, CACHE_LIST_KEY)
        if cached:
            return JSONResponse(content=json.loads(cached))

    # Build dynamic query
    conditions: list[str] = []
    params: list = []
    idx = 1

    if genre:
        conditions.append(f"genre ILIKE ${idx}")
        params.append(f"%{genre}%")
        idx += 1
    if search:
        conditions.append(f"(title ILIKE ${idx} OR author ILIKE ${idx})")
        params.append(f"%{search}%")
        idx += 1
    if available is not None:
        if available:
            conditions.append("available_copies > 0")
        else:
            conditions.append("available_copies = 0")

    where_clause = ("WHERE " + " AND ".join(conditions)) if conditions else ""
    query = f"SELECT * FROM books {where_clause} ORDER BY title"

    async with pool.acquire() as conn:
        rows = await conn.fetch(query, *params)

    result = [dict(r) for r in rows]

    if use_cache and result:
        await set_cached(redis, CACHE_LIST_KEY, json.dumps(result, default=str), ttl=CACHE_LIST_TTL)

    return result


@router.get("/{book_id}", response_model=BookResponse)
async def get_book(
    book_id: int,
    pool=Depends(get_db_pool),
    redis=Depends(get_redis_client),
):
    """Return a single book. Cached for 120 s."""
    key = _item_key(book_id)
    cached = await get_cached(redis, key)
    if cached:
        return JSONResponse(content=json.loads(cached))

    book = await _fetch_book_by_id(pool, book_id)
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")

    await set_cached(redis, key, json.dumps(book, default=str), ttl=CACHE_ITEM_TTL)
    return book


@router.post("", response_model=BookResponse, status_code=201)
async def create_book(
    payload: BookCreate,
    pool=Depends(get_db_pool),
    redis=Depends(get_redis_client),
    _: dict = Depends(require_staff),
):
    """Create a new book and invalidate the list cache."""
    async with pool.acquire() as conn:
        row = await conn.fetchrow(
            """
            INSERT INTO books (title, author, isbn, genre, total_copies, available_copies, published_year)
            VALUES ($1, $2, $3, $4, $5, $5, $6)
            RETURNING *
            """,
            payload.title,
            payload.author,
            payload.isbn,
            payload.genre,
            payload.total_copies,
            payload.published_year,
        )

    await invalidate_cache(redis, CACHE_LIST_KEY)
    return dict(row)


@router.put("/{book_id}", response_model=BookResponse)
async def update_book(
    book_id: int,
    payload: BookUpdate,
    pool=Depends(get_db_pool),
    redis=Depends(get_redis_client),
    _: dict = Depends(require_staff),
):
    """Update book metadata. Invalidates list + item caches."""
    updates: list[str] = []
    params: list = []
    idx = 1

    for field, value in payload.model_dump(exclude_unset=True).items():
        updates.append(f"{field} = ${idx}")
        params.append(value)
        idx += 1

    if not updates:
        raise HTTPException(status_code=400, detail="No fields to update")

    params.append(book_id)
    query = f"UPDATE books SET {', '.join(updates)} WHERE id = ${idx} RETURNING *"

    async with pool.acquire() as conn:
        row = await conn.fetchrow(query, *params)

    if not row:
        raise HTTPException(status_code=404, detail="Book not found")

    await invalidate_cache(redis, CACHE_LIST_KEY)
    await invalidate_cache(redis, _item_key(book_id))
    return dict(row)


@router.patch("/{book_id}/stock", response_model=BookResponse)
async def update_stock(
    book_id: int,
    payload: BookStockDelta,
    pool=Depends(get_db_pool),
    redis=Depends(get_redis_client),
    _: dict = Depends(require_staff),
):
    """
    Atomically adjust available_copies by delta.
    Negative delta (checkout) fails if it would go below 0.
    Positive delta (return) fails if it would exceed total_copies.
    """
    async with pool.acquire() as conn:
        row = await conn.fetchrow(
            """
            UPDATE books
               SET available_copies = available_copies + $1
             WHERE id = $2
               AND available_copies + $1 >= 0
               AND available_copies + $1 <= total_copies
            RETURNING *
            """,
            payload.delta,
            book_id,
        )

    if not row:
        # Determine whether book exists or constraint failed
        async with pool.acquire() as conn:
            exists = await conn.fetchval("SELECT 1 FROM books WHERE id = $1", book_id)
        if not exists:
            raise HTTPException(status_code=404, detail="Book not found")
        raise HTTPException(
            status_code=409,
            detail="Stock update would violate inventory constraints (out of stock or exceeds total)"
        )

    await invalidate_cache(redis, CACHE_LIST_KEY)
    await invalidate_cache(redis, _item_key(book_id))
    return dict(row)


@router.delete("/{book_id}", status_code=204)
async def delete_book(
    book_id: int,
    pool=Depends(get_db_pool),
    redis=Depends(get_redis_client),
    _: dict = Depends(require_staff),
):
    """Delete a book. Returns 409 if active loans exist."""
    async with pool.acquire() as conn:
        # Check active loans
        active = await conn.fetchval(
            "SELECT COUNT(*) FROM borrow_records WHERE book_id = $1 AND status = 'ISSUED'",
            book_id,
        )
        if active:
            raise HTTPException(
                status_code=409,
                detail=f"Cannot delete — {active} active loan(s) exist for this book"
            )

        result = await conn.execute("DELETE FROM books WHERE id = $1", book_id)

    if result == "DELETE 0":
        raise HTTPException(status_code=404, detail="Book not found")

    await invalidate_cache(redis, CACHE_LIST_KEY)
    await invalidate_cache(redis, _item_key(book_id))
