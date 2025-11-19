"""Item API schemas."""
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, HttpUrl


class ItemResponse(BaseModel):
    """Item response schema."""
    id: int
    source_id: int
    title: str
    summary_short: Optional[str] = None
    link: str
    published_at: datetime
    author: Optional[str] = None
    thumbnail_url: Optional[str] = None
    field: Optional[str] = None
    iptc_topics: List[str] = []
    iab_categories: List[str] = []
    custom_tags: List[str] = []
    dup_group_id: Optional[int] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class ItemListResponse(BaseModel):
    """Item list response with pagination."""
    items: List[ItemResponse]
    total: int
    page: int
    page_size: int
    
    class Config:
        from_attributes = True

