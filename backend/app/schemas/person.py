"""Person API schemas."""
from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel


class PersonResponse(BaseModel):
    """Person response schema."""
    id: int
    name: str
    bio: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class PersonCreate(BaseModel):
    """Person creation schema."""
    name: str
    bio: Optional[str] = None


class PersonTimelineEventResponse(BaseModel):
    """Person timeline event response schema."""
    id: int
    person_id: int
    item_id: int
    event_type: str
    description: Optional[str] = None
    created_at: datetime
    
    # Item 정보 (옵션)
    item_title: Optional[str] = None
    item_link: Optional[str] = None
    item_published_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class PersonDetailResponse(BaseModel):
    """Person detail response with timeline and relationship graph."""
    id: int
    name: str
    bio: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    timeline: List[PersonTimelineEventResponse] = []
    relationship_graph: Optional[Dict[str, Any]] = None
    
    class Config:
        from_attributes = True

