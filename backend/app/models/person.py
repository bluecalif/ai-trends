"""Person model for tracked individuals."""
from sqlalchemy import Column, String, Text
from sqlalchemy.orm import relationship

from backend.app.models.base import BaseModel


class Person(BaseModel):
    """Person model for tracking individuals."""

    __tablename__ = "persons"

    name = Column(String(255), unique=True, nullable=False, index=True)
    bio = Column(Text, nullable=True)

    # Relationships
    timeline_events = relationship("PersonTimeline", back_populates="person", cascade="all, delete-orphan")
    watch_rules = relationship("WatchRule", back_populates="person", cascade="all, delete-orphan")

