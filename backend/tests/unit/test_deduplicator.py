"""Unit tests for Deduplicator similarity and grouping helpers."""
from datetime import datetime, timedelta, timezone

import pytest

from backend.app.services.deduplicator import Deduplicator
from backend.app.models.item import Item
from backend.app.models.source import Source


def test_simple_token_similarity():
    d = Deduplicator(db=None)  # only using similarity helper
    assert d._similarity("Deep learning with Transformers", "transformer-based deep learning") > 0.2
    assert d._similarity("GPU acceleration for training", "CPU only training") < 0.5
    assert d._similarity("", "something") == 0.0


def test_process_new_item_assigns_dup_group_id(test_db):
    # Arrange: create a recent seed item
    now = datetime.now(timezone.utc)
    src = Source(title="Src", feed_url="https://example.com/rss", site_url="https://example.com")
    test_db.add(src)
    test_db.flush()
    seed = Item(
        source_id=src.id,
        title="OpenAI releases new GPT model for language tasks",
        summary_short="The model improves performance on a variety of NLP benchmarks.",
        link="https://example.com/a",
        published_at=now - timedelta(days=1),
    )
    test_db.add(seed)
    test_db.flush()

    # A new item with similar content but different link
    new_item = Item(
        source_id=src.id,
        title="New GPT language model released by OpenAI",
        summary_short="Improved performance on NLP tasks is reported by the vendor.",
        link="https://example.com/b",
        published_at=now,
    )
    test_db.add(new_item)
    test_db.flush()

    d = Deduplicator(test_db, similarity_threshold=0.1, lookback_days=7)

    # Act
    group_id = d.process_new_item(new_item)

    # Assert
    test_db.refresh(new_item)
    assert group_id is not None
    assert new_item.dup_group_id == seed.id or new_item.dup_group_id == seed.dup_group_id

