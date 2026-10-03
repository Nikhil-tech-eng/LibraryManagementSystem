from __future__ import annotations
import os
import jwt
from fastapi import Header, HTTPException

def current_user(authorization: str = Header(...)) -> dict:
    token = authorization.removeprefix("Bearer ").strip()
    try:
        return jwt.decode(token, os.getenv("JWT_SECRET_KEY", "change-me-in-production"), algorithms=["HS256"])
    except jwt.PyJWTError as exc:
        raise HTTPException(status_code=401, detail=f"Invalid token: {exc}") from exc

def require_staff(authorization: str = Header(...)) -> dict:
    user = current_user(authorization)
    if user.get("role", "").lower() not in {"admin", "librarian"}:
        raise HTTPException(status_code=403, detail="Admin or librarian access required")
    return user
