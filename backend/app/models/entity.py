"""Entity model for extracted entities."""
from sqlalchemy import Column, String, Enum as SQLEnum
from sqlalchemy.orm import relationship
import enum

from backend.app.models.base import BaseModel


class EntityType(str, enum.Enum):
    """Entity type enumeration."""

    PERSON = "person"
    ORGANIZATION = "org"
    TECHNOLOGY = "tech"


class Entity(BaseModel):
    """Entity model for extracted entities."""

    __tablename__ = "entities"

    name = Column(String(255), unique=True, nullable=False, index=True)
    type = Column(SQLEnum(EntityType), nullable=False, index=True)

    # Relationships
    items = relationship("Item", secondary="item_entities", back_populates="entities")

