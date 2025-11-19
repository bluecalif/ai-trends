"""Watch rule model for person tracking."""
from sqlalchemy import Column, String, Integer, ForeignKey, JSON
from sqlalchemy.orm import relationship

from backend.app.models.base import BaseModel


class WatchRule(BaseModel):
    """Watch rule model for matching items to persons."""

    __tablename__ = "watch_rules"

    label = Column(String(255), nullable=False)
    include_rules = Column(JSON, default=list, nullable=False)  # ["JEPA", "Meta", "LeCun"] (하위 호환)
    exclude_rules = Column(JSON, default=list, nullable=False)  # ["old news"]
    required_keywords = Column(JSON, default=list, nullable=False)  # 필수 키워드 (AND 조건)
    optional_keywords = Column(JSON, default=list, nullable=False)  # 선택 키워드 (OR 조건)
    priority = Column(Integer, default=0, nullable=False)
    person_id = Column(Integer, ForeignKey("persons.id"), nullable=True)

    # Relationships
    person = relationship("Person", back_populates="watch_rules")

