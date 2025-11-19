"""WatchRule API schemas."""
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel


class WatchRuleResponse(BaseModel):
    """WatchRule response schema."""
    id: int
    label: str
    include_rules: List[str] = []
    exclude_rules: List[str] = []
    required_keywords: List[str] = []
    optional_keywords: List[str] = []
    priority: int = 0
    person_id: Optional[int] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class WatchRuleCreate(BaseModel):
    """WatchRule creation schema."""
    label: str
    include_rules: List[str] = []
    exclude_rules: List[str] = []
    required_keywords: List[str] = []
    optional_keywords: List[str] = []
    priority: int = 0
    person_id: Optional[int] = None


class WatchRuleUpdate(BaseModel):
    """WatchRule update schema."""
    label: Optional[str] = None
    include_rules: Optional[List[str]] = None
    exclude_rules: Optional[List[str]] = None
    required_keywords: Optional[List[str]] = None
    optional_keywords: Optional[List[str]] = None
    priority: Optional[int] = None
    person_id: Optional[int] = None

