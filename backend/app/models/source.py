"""Source model for RSS feeds."""
from sqlalchemy import Column, String, Boolean
from sqlalchemy.orm import relationship

from backend.app.models.base import BaseModel


class Source(BaseModel):
    """RSS feed source model."""

    __tablename__ = "sources"

    title = Column(String(255), nullable=False)
    feed_url = Column(String(512), unique=True, nullable=False, index=True)
    site_url = Column(String(512), nullable=True)
    category = Column(String(100), nullable=True)
    lang = Column(String(10), default="en", nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)

    # Relationships
    items = relationship("Item", back_populates="source", cascade="all, delete-orphan")

