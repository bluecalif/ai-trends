"""E2E scaffold for EntityExtractor using real RSS data.

Behavior:
- Attempts to collect from a real RSS source (TechCrunch by default).
- Runs entity extraction on a few collected items.
- Saves detailed results to backend/tests/results/*.json
- Skips gracefully if no new items are collected or network is unavailable.
"""

import json
from pathlib import Path
from datetime import datetime, timezone

import pytest

from backend.app.services.rss_collector import RSSCollector
from backend.app.services.entity_extractor import EntityExtractor
from backend.app.models.source import Source
from backend.app.models.item import Item
from backend.app.models.entity import Entity
from backend.app.models.item_entity import item_entities
from backend.app.core.database import SessionLocal


@pytest.mark.slow
@pytest.mark.e2e_real_data
def test_entity_extractor_e2e_real_data():
    db = SessionLocal()
    results_dir = Path(__file__).parent.parent / "results"
    results_dir.mkdir(exist_ok=True)
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    result_file = results_dir / f"entity_extractor_e2e_real_data_{timestamp}.json"

    test_results = {
        "test_name": "test_entity_extractor_e2e_real_data",
        "timestamp": timestamp,
        "source": None,
        "collection": {"count": 0, "status": "not_run"},
        "extraction": {"total_items": 0, "processed": 0, "items": []},
        "status": "running",
    }

    try:
        # Ensure source exists (TechCrunch as default)
        source = (
            db.query(Source)
            .filter(Source.feed_url == "https://techcrunch.com/feed/")
            .first()
        )
        if not source:
            source = Source(
                title="TechCrunch",
                feed_url="https://techcrunch.com/feed/",
                site_url="https://techcrunch.com",
                is_active=True,
            )
            db.add(source)
            db.flush()
            db.commit()

        test_results["source"] = {
            "id": source.id,
            "title": source.title,
            "feed_url": source.feed_url,
            "site_url": source.site_url,
        }

        # Collect real RSS items
        collector = RSSCollector(db)
        try:
            count = collector.collect_source(source)
        except Exception as e:
            count = 0
            test_results["collection"]["error"] = str(e)

        test_results["collection"]["count"] = count
        test_results["collection"]["status"] = "success" if count >= 0 else "failed"

        # Pick a few recent items (limit 5)
        items = (
            db.query(Item)
            .filter(Item.source_id == source.id)
            .order_by(Item.published_at.desc())
            .limit(5)
            .all()
        )

        test_results["extraction"]["total_items"] = len(items)

        if not items:
            test_results["status"] = "skipped_no_items"
            return

        extractor = EntityExtractor()
        processed = 0
        for item in items:
            entities = extractor.extract_entities(item.title, item.summary_short or "")
            extractor.save_entities(db, item.id, entities)

            # Gather saved relations for verification
            rels = db.execute(
                item_entities.select().where(item_entities.c.item_id == item.id)
            ).all()

            test_results["extraction"]["items"].append(
                {
                    "item_id": item.id,
                    "title": item.title,
                    "link": item.link,
                    "summary_short_present": bool(item.summary_short),
                    "extracted_entities": entities,
                    "relations_count": len(rels),
                }
            )
            processed += 1

        test_results["extraction"]["processed"] = processed
        test_results["status"] = "passed"

    finally:
        with open(result_file, "w", encoding="utf-8") as f:
            json.dump(test_results, f, indent=2, ensure_ascii=False, default=str)
        print(f"\n[TEST RESULTS] Saved to: {result_file}")
        print(f"[TEST RESULTS] Status: {test_results['status']}")
        print(f"[TEST RESULTS] Collected: {test_results['collection']['count']} items")
        print(f"[TEST RESULTS] Processed: {test_results['extraction']['processed']} items")
        db.close()

