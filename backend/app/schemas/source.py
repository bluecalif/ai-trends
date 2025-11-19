"""Source API schemas."""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, HttpUrl


class SourceResponse(BaseModel):
    """Source response schema."""
    id: int
    title: str
    feed_url: str
    site_url: Optional[str] = None
    category: Optional[str] = None
    lang: str = "en"
    is_active: bool = True
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class SourceCreate(BaseModel):
    """Source creation schema."""
    title: str
    feed_url: str
    site_url: Optional[str] = None
    category: Optional[str] = None
    lang: str = "en"
    is_active: bool = True


class SourceUpdate(BaseModel):
    """Source update schema."""
    title: Optional[str] = None
    feed_url: Optional[str] = None
    site_url: Optional[str] = None
    category: Optional[str] = None
    lang: Optional[str] = None
    is_active: Optional[bool] = None

