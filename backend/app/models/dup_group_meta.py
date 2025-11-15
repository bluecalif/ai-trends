from sqlalchemy import Column, Integer, DateTime, ForeignKey, Index
from backend.app.models.base import BaseModel


class DupGroupMeta(BaseModel):
    __tablename__ = "dup_group_meta"

    dup_group_id = Column(Integer, ForeignKey("items.id"), nullable=False, index=True, unique=True)
    first_seen_at = Column(DateTime, nullable=False)
    last_updated_at = Column(DateTime, nullable=False)
    member_count = Column(Integer, nullable=False, default=1)

    __table_args__ = (
        Index("ix_dup_group_meta_first_seen_at", "first_seen_at"),
        Index("ix_dup_group_meta_last_updated_at", "last_updated_at"),
    )


