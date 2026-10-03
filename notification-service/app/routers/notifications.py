"""Notifications router."""
from __future__ import annotations

import logging

import os
import jwt
from fastapi import APIRouter, Depends, HTTPException, Header

from app.database import get_db_pool
from app.mailer import send_checkout_notification, send_return_notification
from app.models import NotificationRequest, NotificationResponse

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/notifications", tags=["notifications"])

def current_user(authorization: str = Header(...)):
    try: return jwt.decode(authorization.removeprefix("Bearer ").strip(), os.getenv("JWT_SECRET_KEY", "change-me-in-production"), algorithms=["HS256"])
    except jwt.PyJWTError as exc: raise HTTPException(401, "Invalid token") from exc


@router.post("/notify", status_code=202)
async def send_notification(payload: NotificationRequest, pool=Depends(get_db_pool)):
    """Send a transactional email and log the result to the DB."""
    status = "SENT"
    try:
        if payload.type in {"checkout", "approved"}:
            await send_checkout_notification(
                email=payload.email,
                book_title=payload.book_title,
                due_date=payload.due_date or "N/A",
                record_id=payload.record_id or 0,
            )
        elif payload.type == "return":
            await send_return_notification(
                email=payload.email,
                book_title=payload.book_title,
                fine_amount=payload.fine_amount or 0.0,
                record_id=payload.record_id or 0,
            )
        elif payload.type == "rejected":
            message = f"Your request for '{payload.book_title}' was rejected by the library staff."
        else:
            raise HTTPException(status_code=400, detail=f"Unknown notification type: {payload.type}")
    except Exception as exc:
        logger.error("Notification send failed: %s", exc)
        status = "FAILED"

    subject = (
        f"Checkout Confirmation: {payload.book_title}"
        if payload.type in {"checkout", "approved"}
        else f"Return Confirmation: {payload.book_title}"
    )

    message = (
        f"Your request for '{payload.book_title}' was approved (due {payload.due_date})."
        if payload.type == "approved" else f"Checkout of '{payload.book_title}' (due {payload.due_date})"
        if payload.type == "checkout"
        else f"Request for '{payload.book_title}' was rejected by library staff."
        if payload.type == "rejected"
        else f"Return of '{payload.book_title}' — fine: ${payload.fine_amount or 0:.2f}"
    )

    message_type = "CHECKOUT" if payload.type in {"checkout", "approved"} else "RETURN_RECEIPT"

    async with pool.acquire() as conn:
        await conn.execute(
            """
            INSERT INTO notifications_log (recipient_email, member_id, subject, message_type, content, status)
            VALUES ($1, $2, $3, $4, $5, $6)
            """,
            payload.email, payload.member_id, subject, message_type, message, status,
        )

    return {"status": status, "message": message}


@router.get("/", response_model=list[NotificationResponse])
async def list_notifications(user=Depends(current_user), pool=Depends(get_db_pool)):
    async with pool.acquire() as conn:
        query = "SELECT id, member_id, message_type as type, content as message, sent_at::text, status FROM notifications_log"
        params = []
        if user.get("role", "").lower() not in {"admin", "librarian"}:
            query += " WHERE member_id=$1"; params.append(int(user["sub"]))
        rows = await conn.fetch(
            query + " ORDER BY sent_at DESC LIMIT 200", *params
        )
    return [dict(r) for r in rows]
