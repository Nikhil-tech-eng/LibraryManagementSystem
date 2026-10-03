"""Pydantic v2 models for user-service."""
from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, EmailStr


class UserRegisterRequest(BaseModel):
    name: str
    email: EmailStr
    password: str
    role: str = "member"


class UserLoginRequest(BaseModel):
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    id: int
    name: str
    email: str
    role: str
    membership_start: Optional[str] = None
    membership_end: Optional[str] = None


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    member_id: int
    role: str


class VerifyTokenResponse(BaseModel):
    valid: bool
    member_id: Optional[int] = None
    email: Optional[str] = None
    role: Optional[str] = None
