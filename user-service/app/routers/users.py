"""User & Auth router for user-service."""
from __future__ import annotations

import logging
import time

from fastapi import APIRouter, Depends, HTTPException, status

from app.auth import (
    create_access_token,
    decode_token,
    get_current_user,
    hash_password,
    verify_password,
)
from app.database import get_db_pool
from app.models import (
    TokenResponse,
    UserLoginRequest,
    UserRegisterRequest,
    UserResponse,
    VerifyTokenResponse,
)
from app.redis_client import blacklist_token, get_redis_client

logger = logging.getLogger(__name__)

router = APIRouter(tags=["users"])


# ---------------------------------------------------------------------------
# Registration
# ---------------------------------------------------------------------------

@router.post("/api/users/register", response_model=UserResponse, status_code=201)
async def register(payload: UserRegisterRequest, pool=Depends(get_db_pool)):
    payload.role = "member"
    hashed = hash_password(payload.password)
    async with pool.acquire() as conn:
        existing = await conn.fetchrow("SELECT id FROM members WHERE email = $1", payload.email)
        if existing:
            raise HTTPException(status_code=409, detail="Email already registered")
        row = await conn.fetchrow(
            """
            INSERT INTO members (full_name, email, password_hash, role)
            VALUES ($1, $2, $3, $4)
            RETURNING id, full_name as name, email, role, membership_status, created_at::text as membership_start
            """,
            payload.name, payload.email, hashed, payload.role,
        )
    return dict(row)


# ---------------------------------------------------------------------------
# Login
# ---------------------------------------------------------------------------

@router.post("/api/users/login", response_model=TokenResponse)
async def login(payload: UserLoginRequest, pool=Depends(get_db_pool)):
    async with pool.acquire() as conn:
        member = await conn.fetchrow(
            "SELECT id, email, password_hash, role FROM members WHERE email = $1", payload.email
        )
    if not member or not verify_password(payload.password, member["password_hash"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    result = create_access_token(member["id"], member["email"], member["role"])
    return TokenResponse(
        access_token=result["token"],
        member_id=member["id"],
        role=member["role"],
    )


# ---------------------------------------------------------------------------
# Token verification (called by borrowing-service)
# ---------------------------------------------------------------------------

@router.get("/auth/verify", response_model=VerifyTokenResponse)
@router.post("/auth/verify", response_model=VerifyTokenResponse)
async def verify_token(
    current_user: dict = Depends(get_current_user),
):
    return VerifyTokenResponse(
        valid=True,
        member_id=int(current_user["sub"]),
        email=current_user["email"],
        role=current_user["role"],
    )


# ---------------------------------------------------------------------------
# Logout — blacklist the JTI
# ---------------------------------------------------------------------------

@router.post("/api/users/logout", status_code=204)
async def logout(
    current_user: dict = Depends(get_current_user),
    redis=Depends(get_redis_client),
):
    jti = current_user.get("jti")
    exp = current_user.get("exp", 0)
    remaining = max(int(exp - time.time()), 1)
    if jti:
        await blacklist_token(jti, remaining)


# ---------------------------------------------------------------------------
# Me / list
# ---------------------------------------------------------------------------

@router.get("/api/users/me", response_model=UserResponse)
async def me(current_user: dict = Depends(get_current_user), pool=Depends(get_db_pool)):
    async with pool.acquire() as conn:
        row = await conn.fetchrow(
            "SELECT id, full_name as name, email, role, membership_status, created_at::text as membership_start FROM members WHERE id = $1",
            int(current_user["sub"]),
        )
    if not row:
        raise HTTPException(status_code=404, detail="Member not found")
    return dict(row)


@router.get("/api/users", response_model=list[UserResponse])
async def list_users(
    current_user: dict = Depends(get_current_user),
    pool=Depends(get_db_pool),
):
    if current_user.get("role", "").lower() not in {"librarian", "admin"}:
        raise HTTPException(status_code=403, detail="Admin or librarian access required")
    async with pool.acquire() as conn:
        rows = await conn.fetch(
            "SELECT id, full_name as name, email, role, membership_status, created_at::text as membership_start FROM members ORDER BY full_name"
        )
    return [dict(r) for r in rows]
