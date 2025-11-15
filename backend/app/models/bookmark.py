"""Bookmark model for user bookmarks."""
from sqlalchemy import Column, Integer, ForeignKey, String, JSON, Text

from backend.app.models.base import BaseModel


class Bookmark(BaseModel):
    """User bookmark model."""

    __tablename__ = "bookmarks"

    item_id = Column(Integer, ForeignKey("items.id"), nullable=False, index=True)
    title = Column(String(512), nullable=False)
    tags = Column(JSON, default=list, nullable=False)
    note = Column(Text, nullable=True)

