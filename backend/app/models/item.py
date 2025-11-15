"""Item model for collected news items."""
from sqlalchemy import Column, String, Text, Integer, ForeignKey, DateTime, JSON
from sqlalchemy.orm import relationship

from backend.app.models.base import BaseModel


class Item(BaseModel):
    """News item model."""

    __tablename__ = "items"

    source_id = Column(Integer, ForeignKey("sources.id"), nullable=False, index=True)
    title = Column(String(512), nullable=False, index=True)
    summary_short = Column(Text, nullable=True)
    link = Column(String(1024), unique=True, nullable=False, index=True)
    published_at = Column(DateTime, nullable=False, index=True)
    author = Column(String(255), nullable=True)
    thumbnail_url = Column(String(1024), nullable=True)

    # Classification tags (JSON arrays)
    iptc_topics = Column(JSON, default=list, nullable=False)
    iab_categories = Column(JSON, default=list, nullable=False)
    custom_tags = Column(JSON, default=list, nullable=False)

    # Deduplication grouping
    dup_group_id = Column(Integer, nullable=True, index=True)

    # Relationships
    source = relationship("Source", back_populates="items")
    entities = relationship("Entity", secondary="item_entities", back_populates="items")

