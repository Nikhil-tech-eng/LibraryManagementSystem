from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class BookCreate(BaseModel):
    title: str = Field(..., min_length=1)
    author: str = Field(..., min_length=1)
    isbn: str = Field(..., min_length=5)
    genre: str = Field(..., min_length=1)
    published_year: Optional[int] = 2024
    total_copies: Optional[int] = 1
    available_copies: Optional[int] = 1
    cover_image_url: Optional[str] = "https://images.unsplash.com/photo-1544716278-ca5e3f4abd8c?w=500&auto=format&fit=crop&q=80"
    description: Optional[str] = ""

class BookUpdate(BaseModel):
    title: Optional[str] = None
    author: Optional[str] = None
    isbn: Optional[str] = None
    genre: Optional[str] = None
    published_year: Optional[int] = None
    total_copies: Optional[int] = None
    available_copies: Optional[int] = None
    cover_image_url: Optional[str] = None
    description: Optional[str] = None

class BookStockDelta(BaseModel):
    delta: int # -1 for checkout, +1 for return

class BookResponse(BaseModel):
    id: int
    title: str
    author: str
    isbn: str
    genre: str
    published_year: int
    total_copies: int
    available_copies: int
    cover_image_url: Optional[str] = None
    description: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
