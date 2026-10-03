from __future__ import annotations
from datetime import date, datetime, timezone
from fastapi import APIRouter, Depends, Header, HTTPException
from app.database import get_db_pool
from app.http_client import get_book, notify, patch_book_stock, verify_token
from app.models import BookRequest, BorrowRecordResponse, BorrowStatsResponse, DashboardResponse

router = APIRouter(prefix="/api/borrow", tags=["borrowing"])
STAFF = {"admin", "librarian"}
COLS = "br.id,br.member_id,br.book_id,m.full_name member_name,b.title book_title,b.author book_author,br.borrow_date::text request_date,br.borrow_date::text issue_date,br.due_date::text,br.return_date::text,br.status,br.fine_amount::float"

async def identity(authorization: str = Header(...)):
    return await verify_token(authorization.removeprefix("Bearer ").strip())
def staff(user):
    if user.get("role", "").lower() not in STAFF: raise HTTPException(403, "Admin or librarian access required")
async def rows(conn, where="", *args):
    data = [dict(r) for r in await conn.fetch(f"SELECT {COLS} FROM borrow_records br JOIN members m ON m.id=br.member_id JOIN books b ON b.id=br.book_id {where} ORDER BY br.borrow_date DESC", *args)]
    for item in data:
        if item["status"] == "ISSUED" and item["due_date"] and datetime.fromisoformat(str(item["due_date"]).replace("Z", "+00:00")) < datetime.now(timezone.utc): item["status"] = "OVERDUE"
    return data
async def email(pool, member_id):
    async with pool.acquire() as conn: return await conn.fetchval("SELECT email FROM members WHERE id=$1", member_id)

@router.post("/request", response_model=BorrowRecordResponse, status_code=201)
async def request_book(payload: BookRequest, user=Depends(identity), pool=Depends(get_db_pool)):
    if user.get("role", "").lower() != "member": raise HTTPException(403, "Members only")
    book = await get_book(payload.book_id)
    if book.get("available_copies", 0) < 1: raise HTTPException(409, "No copies available")
    async with pool.acquire() as conn:
        if await conn.fetchval("SELECT 1 FROM borrow_records WHERE member_id=$1 AND book_id=$2 AND status IN ('PENDING','ISSUED')", user["member_id"], payload.book_id): raise HTTPException(409, "You already have a pending request or issued copy")
        record = await conn.fetchrow("INSERT INTO borrow_records(member_id,book_id,due_date,status) VALUES($1,$2,NULL,'PENDING') RETURNING id", user["member_id"], payload.book_id)
        return (await rows(conn, "WHERE br.id=$1", record["id"]))[0]

@router.get("/my-loans", response_model=list[BorrowRecordResponse])
async def my_loans(user=Depends(identity), pool=Depends(get_db_pool)):
    if user.get("role", "").lower() != "member": raise HTTPException(403, "Members only")
    async with pool.acquire() as conn: return await rows(conn, "WHERE br.member_id=$1", user["member_id"])

@router.get("/pending", response_model=list[BorrowRecordResponse])
async def pending(user=Depends(identity), pool=Depends(get_db_pool)):
    staff(user)
    async with pool.acquire() as conn: return await rows(conn, "WHERE br.status='PENDING'")

@router.post("/{record_id}/approve", response_model=BorrowRecordResponse)
async def approve(record_id: int, user=Depends(identity), pool=Depends(get_db_pool)):
    staff(user)
    async with pool.acquire() as conn:
        record = await conn.fetchrow("SELECT * FROM borrow_records WHERE id=$1 AND status='PENDING'", record_id)
        if not record: raise HTTPException(404, "Pending request not found")
        book = await get_book(record["book_id"])
        if book.get("available_copies", 0) < 1: raise HTTPException(409, "No copies available")
        await patch_book_stock(record["book_id"], -1)
        await conn.execute("UPDATE borrow_records SET status='ISSUED',borrow_date=CURRENT_TIMESTAMP,due_date=CURRENT_TIMESTAMP+INTERVAL '14 days' WHERE id=$1", record_id)
        result = (await rows(conn, "WHERE br.id=$1", record_id))[0]
    await notify({"member_id": result["member_id"], "email": await email(pool, result["member_id"]), "type": "approved", "book_title": result["book_title"], "due_date": result["due_date"], "record_id": record_id})
    return result

@router.post("/{record_id}/reject", response_model=BorrowRecordResponse)
async def reject(record_id: int, user=Depends(identity), pool=Depends(get_db_pool)):
    staff(user)
    async with pool.acquire() as conn:
        updated = await conn.fetchrow("UPDATE borrow_records SET status='REJECTED' WHERE id=$1 AND status='PENDING' RETURNING id", record_id)
        if not updated: raise HTTPException(404, "Pending request not found")
        result = (await rows(conn, "WHERE br.id=$1", record_id))[0]
    await notify({"member_id": result["member_id"], "email": await email(pool, result["member_id"]), "type": "rejected", "book_title": result["book_title"], "record_id": record_id})
    return result

@router.get("/active", response_model=list[BorrowRecordResponse])
async def active(user=Depends(identity), pool=Depends(get_db_pool)):
    staff(user)
    async with pool.acquire() as conn: return await rows(conn, "WHERE br.status='ISSUED'")

@router.post("/{record_id}/return", response_model=BorrowRecordResponse)
async def mark_returned(record_id: int, user=Depends(identity), pool=Depends(get_db_pool)):
    staff(user)
    async with pool.acquire() as conn:
        record = await conn.fetchrow("SELECT * FROM borrow_records WHERE id=$1 AND status='ISSUED'", record_id)
        if not record: raise HTTPException(404, "Active loan not found")
        due = record["due_date"].date() if isinstance(record["due_date"], datetime) else date.fromisoformat(str(record["due_date"])[:10])
        fine = max((date.today()-due).days, 0)
        await conn.execute("UPDATE borrow_records SET status='RETURNED',return_date=CURRENT_TIMESTAMP,fine_amount=$1 WHERE id=$2", fine, record_id)
        result = (await rows(conn, "WHERE br.id=$1", record_id))[0]
    await patch_book_stock(record["book_id"], 1)
    await notify({"member_id": result["member_id"], "email": await email(pool, result["member_id"]), "type": "return", "book_title": result["book_title"], "fine_amount": fine, "record_id": record_id})
    return result

@router.get("/stats", response_model=BorrowStatsResponse)
async def stats(user=Depends(identity), pool=Depends(get_db_pool)):
    staff(user)
    async with pool.acquire() as conn: return BorrowStatsResponse(total_active=await conn.fetchval("SELECT COUNT(*) FROM borrow_records WHERE status='ISSUED'"), total_overdue=await conn.fetchval("SELECT COUNT(*) FROM borrow_records WHERE status='ISSUED' AND due_date<CURRENT_TIMESTAMP"), total_returned=await conn.fetchval("SELECT COUNT(*) FROM borrow_records WHERE status='RETURNED'"))

@router.get("/admin/dashboard", response_model=DashboardResponse)
async def dashboard(user=Depends(identity), pool=Depends(get_db_pool)):
    staff(user)
    async with pool.acquire() as conn:
        activity = await conn.fetch("SELECT br.id,br.status,br.borrow_date::text event_date,m.full_name member_name,b.title book_title FROM borrow_records br JOIN members m ON m.id=br.member_id JOIN books b ON b.id=br.book_id ORDER BY br.created_at DESC LIMIT 10")
        return DashboardResponse(total_books=await conn.fetchval("SELECT COUNT(*) FROM books"), total_available_copies=await conn.fetchval("SELECT COALESCE(SUM(available_copies),0) FROM books"), active_issued_loans=await conn.fetchval("SELECT COUNT(*) FROM borrow_records WHERE status='ISSUED'"), pending_requests=await conn.fetchval("SELECT COUNT(*) FROM borrow_records WHERE status='PENDING'"), overdue_loans=await conn.fetchval("SELECT COUNT(*) FROM borrow_records WHERE status='ISSUED' AND due_date<CURRENT_TIMESTAMP"), total_members=await conn.fetchval("SELECT COUNT(*) FROM members WHERE role='member'"), recent_activity=[dict(r) for r in activity])
