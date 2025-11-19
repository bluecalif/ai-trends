"""Bookmark API schemas."""
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel


class BookmarkResponse(BaseModel):
    """Bookmark response schema."""
    id: int
    item_id: int
    title: str
    tags: List[str] = []
    note: Optional[str] = None
    created_at: datetime
    
    # Item 정보 (옵션)
    item_title: Optional[str] = None
    item_link: Optional[str] = None
    item_published_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class BookmarkCreate(BaseModel):
    """Bookmark creation schema."""
    item_id: Optional[int] = None
    link: Optional[str] = None
    title: str
    tags: List[str] = []
    note: Optional[str] = None


class BookmarkUpdate(BaseModel):
    """Bookmark update schema."""
    title: Optional[str] = None
    tags: Optional[List[str]] = None
    note: Optional[str] = None

