"""Integration test for EntityExtractor save_entities (DB relation)."""
from unittest.mock import Mock
import json

from sqlalchemy.orm import Session

from backend.app.services.entity_extractor import EntityExtractor
from backend.app.models.source import Source
from backend.app.models.item import Item
from backend.app.models.entity import Entity, EntityType
from backend.app.models.item_entity import item_entities


class DummyChoices:
    def __init__(self, content: str):
        msg = Mock()
        msg.content = content
        choice = Mock()
        choice.message = msg
        self.choices = [choice]


def test_save_entities_creates_records_and_relations(test_db: Session):
    # Arrange: create source and item
    source = Source(title="Test", feed_url="https://example.com/rss", site_url="https://example.com")
    test_db.add(source)
    test_db.flush()

    item = Item(
        source_id=source.id,
        title="Test Item",
        summary_short="Meta and Yann LeCun discuss JEPA model.",
        link="https://example.com/article",
        published_at=__import__("datetime").datetime.utcnow(),
    )
    test_db.add(item)
    test_db.flush()

    extractor = EntityExtractor()

    # Mock response
    payload = {
        "entities": [
            {"name": "Yann LeCun", "type": "person"},
            {"name": "Meta", "type": "org"},
            {"name": "JEPA", "type": "tech"},
        ]
    }
    extractor.client.chat.completions.create = Mock(
        return_value=DummyChoices(json.dumps(payload))
    )

    entities = extractor.extract_entities(item.title, item.summary_short or "")
    assert len(entities) == 3

    # Act: save entities and relations
    extractor.save_entities(test_db, item.id, entities)

    # Assert: entities exist
    names = {e["name"] for e in entities}
    db_entities = test_db.query(Entity).filter(Entity.name.in_(list(names))).all()
    assert len(db_entities) == 3

    # Assert: relations exist
    for e in db_entities:
        rel = test_db.execute(
            item_entities.select().where(
                (item_entities.c.item_id == item.id) & (item_entities.c.entity_id == e.id)
            )
        ).first()
        assert rel is not None


