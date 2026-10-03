from __future__ import annotations
from typing import Optional
from pydantic import BaseModel
class BookRequest(BaseModel): book_id: int
class BorrowRecordResponse(BaseModel):
    id: int; member_id: int; book_id: int; member_name: Optional[str] = None; book_title: Optional[str] = None; book_author: Optional[str] = None; request_date: Optional[str] = None; issue_date: Optional[str] = None; due_date: Optional[str] = None; return_date: Optional[str] = None; status: str; fine_amount: Optional[float] = None
class BorrowStatsResponse(BaseModel):
    total_active: int; total_overdue: int; total_returned: int
class DashboardResponse(BaseModel):
    total_books: int; total_available_copies: int; active_issued_loans: int; pending_requests: int; overdue_loans: int; total_members: int; recent_activity: list[dict]
