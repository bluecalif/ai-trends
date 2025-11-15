"""Person timeline model for tracking events."""
from sqlalchemy import Column, String, Integer, ForeignKey, Text
from sqlalchemy.orm import relationship

from backend.app.models.base import BaseModel


class PersonTimeline(BaseModel):
    """Person timeline event model."""

    __tablename__ = "person_timeline"

    person_id = Column(Integer, ForeignKey("persons.id"), nullable=False, index=True)
    item_id = Column(Integer, ForeignKey("items.id"), nullable=False, index=True)
    event_type = Column(String(50), nullable=False)  # paper, product, investment, etc.
    description = Column(Text, nullable=True)

    # Relationships
    person = relationship("Person", back_populates="timeline_events")

