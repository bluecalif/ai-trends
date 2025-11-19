"""Insights API schemas."""
from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel


class KeywordTrendResponse(BaseModel):
    """Keyword trend response schema."""
    keyword: str
    current_count: int
    previous_count: int
    change: int
    change_percent: float


class PersonInsightResponse(BaseModel):
    """Person insight response schema."""
    person_id: int
    person_name: str
    event_type_counts: Dict[str, int]
    recent_events: List[Dict[str, Any]] = []


class WeeklyInsightResponse(BaseModel):
    """Weekly insight response schema."""
    week_start: datetime
    week_end: datetime
    top_keywords: List[KeywordTrendResponse] = []
    person_insights: List[PersonInsightResponse] = []
    summary: Optional[str] = None

