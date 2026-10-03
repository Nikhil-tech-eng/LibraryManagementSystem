# Database & Caching Architecture Documentation

## Overview
The Library Management System (LMS) uses **PostgreSQL 15+** as the persistent relational source of truth and **Redis 7+** as an in-memory caching and session invalidation layer.

---

## 1. PostgreSQL Schema Architecture

| Table | Description | Primary Key | Critical Indexes |
|---|---|---|---|
| `books` | Book titles, authors, genres, inventory levels | `id` (SERIAL) | `isbn` (UNIQUE), `genre` |
| `members` | Library members and staff credentials | `id` (SERIAL) | `email` (UNIQUE) |
| `borrow_records` | Active & historical loans, due dates, fines | `id` (SERIAL) | `member_id`, `book_id`, `status` |
| `notifications_log` | Transactional email audit trail | `id` (SERIAL) | `recipient_email` |

---

## 2. Redis Caching & Invalidation Architecture

Redis operates in a **Cache-Aside (Lazy Loading)** topology to minimize PostgreSQL query latency during high-traffic checkout and browsing surges.

### Redis Key Naming Conventions

| Key Pattern | Data Structure | TTL | Purpose | Invalidation Triggers |
|---|---|---|---|---|
| `cache:books:list` | String (JSON) | 60s | Cached global catalog response for `GET /books` | `POST /books`, `PUT /books/{id}`, `PATCH /books/{id}/stock`, `DELETE /books/{id}` |
| `cache:books:{id}` | String (JSON) | 120s | Single book detail cache for `GET /books/{id}` | Any book mutation or stock change |
| `session:blacklist:{jti}` | String | 24h | Blacklisted JWT identifiers revoked upon logout | `POST /api/users/logout` |
| `stats:circulation` | Hash | 30s | Aggregate metrics (active, overdue, returned) | Automatically refreshed by `borrowing-service` |

### Cache-Aside Logic for `GET /books`
1. Request hits `book-catalog` service.
2. If unfiltered query: Check Redis `GET cache:books:list`.
   - **Cache HIT:** Return cached JSON immediately (typically < 1.5ms).
   - **Cache MISS:** Execute PostgreSQL query, serialize rows, store in Redis with 60s TTL (`SETEX cache:books:list 60 <data>`), and return response.
3. On any write (`POST /books`, checkout, return): `DEL cache:books:list` is executed immediately.
