"""Entity extraction service (persons, organizations, technologies).

MVP scope:
- Implement OpenAI-based extractor returning a simple list of entities.
- Provide DB save helper to upsert entities and link to items.

Testing strategy:
- Unit tests will mock OpenAI client.
- Integration tests will verify DB persistence and relation creation.
"""

from typing import List, Dict
import json

from sqlalchemy.orm import Session

from backend.app.core.config import get_settings
from backend.app.models.entity import Entity, EntityType
from backend.app.models.item_entity import item_entities


class EntityExtractor:
    """Extract entities (person/org/tech) from title + summary."""

    def __init__(self):
        """Initialize OpenAI client using configured API key."""
        settings = get_settings()
        if not settings.OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY is not set in environment variables")

        # Deferred import to avoid dependency when not used in tests
        from openai import OpenAI

        self.client = OpenAI(api_key=settings.OPENAI_API_KEY)

    def extract_entities(self, title: str, summary: str) -> List[Dict]:
        """Call OpenAI to extract entities as list of {name, type} dicts.

        Returns:
            List of entities where type is one of: person | org | tech
        """
        prompt = (
            "다음 기사에서 중요한 엔티티를 추출하세요:\n"
            "- 인물 (Person): 연구자, 기업가, 전문가 이름\n"
            "- 기관 (Organization): 회사, 연구소, 대학\n"
            "- 기술 (Technology): 기술명, 모델명, 프레임워크\n\n"
            f"제목: {title}\n"
            f"요약: {summary}\n\n"
            "JSON 형식으로 반환:\n"
            "{\n"
            '  "entities": [\n'
            '    {"name": "Yann LeCun", "type": "person"},\n'
            '    {"name": "Meta", "type": "org"},\n'
            '    {"name": "JEPA", "type": "tech"}\n'
            "  ]\n"
            "}\n"
        )

        response = self.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"},
            max_tokens=300,
            temperature=0.0,
        )

        try:
            result = json.loads(response.choices[0].message.content)
        except Exception:
            return []

        entities = result.get("entities", [])
        valid_entities: List[Dict] = []
        for e in entities:
            name = (e.get("name") or "").strip()
            type_str = (e.get("type") or "").strip().lower()
            if not name or type_str not in {"person", "org", "tech"}:
                continue
            valid_entities.append({"name": name, "type": type_str})
        return valid_entities

    def save_entities(self, db: Session, item_id: int, entities: List[Dict]) -> None:
        """Upsert entities and create item-entity relations if missing."""
        for entity_data in entities:
            name = entity_data.get("name")
            type_str = entity_data.get("type")
            if not name or not type_str:
                continue

            entity = (
                db.query(Entity)
                .filter(Entity.name == name)
                .first()
            )

            if not entity:
                # Map string to enum; upper() matches enum names PERSON/ORGANIZATION/TECHNOLOGY
                enum_map = {"person": "PERSON", "org": "ORGANIZATION", "tech": "TECHNOLOGY"}
                try:
                    entity_type = EntityType[enum_map[type_str]]
                except Exception:
                    # Skip unknown type
                    continue

                entity = Entity(name=name, type=entity_type)
                db.add(entity)
                db.flush()

            existing = db.execute(
                item_entities.select().where(
                    (item_entities.c.item_id == item_id)
                    & (item_entities.c.entity_id == entity.id)
                )
            ).first()

            if not existing:
                db.execute(
                    item_entities.insert().values(item_id=item_id, entity_id=entity.id)
                )

        db.commit()

