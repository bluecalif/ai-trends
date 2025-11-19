"""E2E scaffold for ClassifierService using real RSS data.
Saves results to backend/tests/results/*.json
"""
import json
from pathlib import Path
from datetime import datetime, timezone

import pytest

from backend.app.services.rss_collector import RSSCollector
from backend.app.services.classifier import ClassifierService
from backend.app.models.source import Source
from backend.app.models.item import Item
from backend.app.core.database import SessionLocal


@pytest.mark.slow
@pytest.mark.e2e_real_data
def test_classifier_e2e_real_data():
    db = SessionLocal()
    results_dir = Path(__file__).parent.parent / "results"
    results_dir.mkdir(exist_ok=True)
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    result_file = results_dir / f"classifier_e2e_real_data_{timestamp}.json"

    test_results = {
        "test_name": "test_classifier_e2e_real_data",
        "timestamp": timestamp,
        "source": None,
        "collection": {"count": 0, "status": "not_run"},
        "classification": {"total_items": 0, "processed": 0, "items": []},
        "status": "running",
    }

    try:
        # Ensure source (TechCrunch)
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

        # Get existing items from Supabase actual DB (skip collection, use existing data)
        existing_item_count = db.query(Item).filter(Item.source_id == source.id).count()
        test_results["collection"]["count"] = existing_item_count
        test_results["collection"]["status"] = "using_existing_data"
        
        if existing_item_count == 0:
            # If no existing data, try to collect
            print("[Classifier E2E] No existing items, attempting collection...")
            collector = RSSCollector(db)
            try:
                count = collector.collect_source(source)
                test_results["collection"]["count"] = count
                test_results["collection"]["status"] = "collected_new"
            except Exception as e:
                count = 0
                test_results["collection"]["error"] = str(e)
                test_results["collection"]["status"] = "collection_failed"

        # Pick recent items from actual DB (limit 5)
        items = (
            db.query(Item)
            .filter(Item.source_id == source.id)
            .order_by(Item.published_at.desc())
            .limit(5)
            .all()
        )
        test_results["classification"]["total_items"] = len(items)
        if not items:
            test_results["status"] = "skipped_no_items"
            return

        svc = ClassifierService()
        processed = 0
        for it in items:
            result = svc.classify(it.title, it.summary_short or "")
            it.field = result.get("field")
            it.iptc_topics = result["iptc_topics"]
            it.iab_categories = result["iab_categories"]
            it.custom_tags = result["custom_tags"]
            processed += 1

            test_results["classification"]["items"].append(
                {
                    "item_id": it.id,
                    "title": it.title,
                    "summary_short_present": bool(it.summary_short),
                    "summary_short_length": len(it.summary_short) if it.summary_short else 0,
                    "custom_tags": it.custom_tags,
                    "iptc_topics": it.iptc_topics,
                    "iab_categories": it.iab_categories,
                }
            )

        db.commit()
        test_results["classification"]["processed"] = processed
        test_results["status"] = "passed"

    finally:
        with open(result_file, "w", encoding="utf-8") as f:
            json.dump(test_results, f, indent=2, ensure_ascii=False, default=str)
        print(f"\n[TEST RESULTS] Saved to: {result_file}")
        print(f"[TEST RESULTS] Status: {test_results['status']}")
        print(f"[TEST RESULTS] Collected: {test_results['collection']['count']} items")
        print(f"[TEST RESULTS] Processed: {test_results['classification']['processed']} items")
        db.close()

