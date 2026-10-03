"""Pydantic v2 models for notification-service."""
from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, EmailStr


class NotificationRequest(BaseModel):
    member_id: int
    email: EmailStr
    type: str                      # "approved" | "rejected" | "return"
    book_title: str
    due_date: Optional[str] = None
    fine_amount: Optional[float] = None
    record_id: Optional[int] = None


class NotificationResponse(BaseModel):
    id: int
    member_id: int
    type: str
    message: str
    sent_at: Optional[str] = None
    status: str
