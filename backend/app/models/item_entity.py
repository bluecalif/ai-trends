"""Item-Entity many-to-many relationship table."""
from sqlalchemy import Table, Column, Integer, ForeignKey

from backend.app.models.base import Base

item_entities = Table(
    "item_entities",
    Base.metadata,
    Column("item_id", Integer, ForeignKey("items.id"), primary_key=True),
    Column("entity_id", Integer, ForeignKey("entities.id"), primary_key=True),
)

