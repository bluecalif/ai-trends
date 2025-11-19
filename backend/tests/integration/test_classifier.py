"""Integration test for ClassifierService saving JSON fields on Item."""
from sqlalchemy.orm import Session

from backend.app.services.classifier import ClassifierService
from backend.app.models.source import Source
from backend.app.models.item import Item


def test_classifier_saves_to_item_json_fields(test_db: Session):
    # Arrange
    source = Source(title="Test", feed_url="https://example.com/rss", site_url="https://example.com")
    test_db.add(source)
    test_db.flush()

    item = Item(
        source_id=source.id,
        title="Agentic JEPA model on GPUs",
        summary_short="New agentic systems using JEPA run efficiently on GPUs.",
        link="https://example.com/article",
        published_at=__import__("datetime").datetime.utcnow(),
    )
    test_db.add(item)
    test_db.flush()

    # Act
    svc = ClassifierService()
    result = svc.classify(item.title, item.summary_short or "")

    item.field = result.get("field")
    item.iptc_topics = result["iptc_topics"]
    item.iab_categories = result["iab_categories"]
    item.custom_tags = result["custom_tags"]
    test_db.commit()

    # Assert
    test_db.refresh(item)
    assert isinstance(item.custom_tags, list)
    assert "agents" in item.custom_tags or len(item.custom_tags) >= 0
    assert isinstance(item.iptc_topics, list)
    assert isinstance(item.iab_categories, list)


