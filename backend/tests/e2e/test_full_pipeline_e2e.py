"""E2E test for full pipeline: RSS collection → processing → API → frontend simulation.

This test verifies the complete data flow from RSS collection through all processing
steps to API availability.
"""

from datetime import datetime, timezone, timedelta
from pathlib import Path
import json
import pytest

from fastapi.testclient import TestClient

from backend.app.main import app
from backend.app.core.database import SessionLocal
from backend.app.core.constants import PRD_RSS_SOURCES
from backend.app.services.rss_collector import RSSCollector
from backend.app.services.summarizer import Summarizer
from backend.app.services.classifier import Classifier
from backend.app.services.entity_extractor import EntityExtractor
from backend.app.services.deduplicator import Deduplicator
from backend.app.services.person_tracker import PersonTracker
from backend.app.models.source import Source
from backend.app.models.item import Item


@pytest.mark.slow
@pytest.mark.e2e_real_data
def test_full_pipeline_e2e():
    """E2E test for complete pipeline with real database data."""
    client = TestClient(app)
    db = SessionLocal()
    results_dir = Path(__file__).parent.parent / "results"
    results_dir.mkdir(exist_ok=True)
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    result_file = results_dir / f"full_pipeline_e2e_{timestamp}.json"

    test_results = {
        "test_name": "test_full_pipeline_e2e",
        "timestamp": timestamp,
        "pipeline_steps": {
            "rss_collection": {"status": "running", "items_collected": 0},
            "summarization": {"status": "running", "items_processed": 0},
            "classification": {"status": "running", "items_processed": 0},
            "entity_extraction": {"status": "running", "items_processed": 0},
            "grouping": {"status": "running", "groups_created": 0},
            "person_tracking": {"status": "running", "matches_found": 0},
            "api_verification": {"status": "running", "endpoints_tested": 0},
        },
        "status": "running",
    }

    try:
        # Step 1: Ensure sources exist
        print("[Full Pipeline E2E] Step 1: Ensuring sources exist...")
        sources_created = 0
        for source_data in PRD_RSS_SOURCES:
            source = db.query(Source).filter(
                Source.feed_url == source_data["feed_url"]
            ).first()
            if not source:
                source = Source(
                    title=source_data["title"],
                    feed_url=source_data["feed_url"],
                    site_url=source_data.get("site_url"),
                    is_active=True,
                )
                db.add(source)
                sources_created += 1
            else:
                source.is_active = True
        db.commit()
        print(f"[Full Pipeline E2E] Sources ready: {sources_created} created")

        # Step 2: Get existing items or collect new ones
        print("[Full Pipeline E2E] Step 2: Getting items from DB...")
        items = db.query(Item).order_by(Item.published_at.desc()).limit(50).all()
        
        if len(items) == 0:
            print("[Full Pipeline E2E] No items in DB, collecting from active sources...")
            collector = RSSCollector(db)
            active_sources = db.query(Source).filter(Source.is_active == True).all()
            total_collected = 0
            for source in active_sources[:3]:  # Limit to 3 sources for speed
                try:
                    count = collector.collect_source(source)
                    total_collected += count
                    print(f"[Full Pipeline E2E] Collected {count} items from {source.title}")
                except Exception as e:
                    print(f"[Full Pipeline E2E] Error collecting from {source.title}: {e}")
            test_results["pipeline_steps"]["rss_collection"]["items_collected"] = total_collected
            items = db.query(Item).order_by(Item.published_at.desc()).limit(50).all()
        else:
            test_results["pipeline_steps"]["rss_collection"]["items_collected"] = 0
            print(f"[Full Pipeline E2E] Using {len(items)} existing items")

        assert len(items) > 0, "E2E 테스트는 반드시 아이템이 있어야 함. 소스 등록 및 RSS 수집을 먼저 실행하세요."
        test_results["pipeline_steps"]["rss_collection"]["status"] = "completed"

        # Step 3: Summarization
        print("[Full Pipeline E2E] Step 3: Running summarization...")
        summarizer = Summarizer()
        items_to_summarize = [item for item in items if not item.summary_short][:10]
        summarized_count = 0
        for item in items_to_summarize:
            try:
                summary = summarizer.summarize(item.title, item.summary_short or "", item.link)
                item.summary_short = summary
                summarized_count += 1
            except Exception as e:
                print(f"[Full Pipeline E2E] Error summarizing item {item.id}: {e}")
        db.commit()
        test_results["pipeline_steps"]["summarization"]["items_processed"] = summarized_count
        test_results["pipeline_steps"]["summarization"]["status"] = "completed"
        print(f"[Full Pipeline E2E] Summarized {summarized_count} items")

        # Step 4: Classification
        print("[Full Pipeline E2E] Step 4: Running classification...")
        classifier = Classifier()
        items_to_classify = [item for item in items if not item.custom_tags][:10]
        classified_count = 0
        for item in items_to_classify:
            try:
                classification = classifier.classify(item.title, item.summary_short or "")
                item.iptc_topics = classification.get("iptc_topics", [])
                item.iab_categories = classification.get("iab_categories", [])
                item.custom_tags = classification.get("custom_tags", [])
                item.field = classification.get("field")
                classified_count += 1
            except Exception as e:
                print(f"[Full Pipeline E2E] Error classifying item {item.id}: {e}")
        db.commit()
        test_results["pipeline_steps"]["classification"]["items_processed"] = classified_count
        test_results["pipeline_steps"]["classification"]["status"] = "completed"
        print(f"[Full Pipeline E2E] Classified {classified_count} items")

        # Step 5: Entity Extraction
        print("[Full Pipeline E2E] Step 5: Running entity extraction...")
        entity_extractor = EntityExtractor()
        items_to_extract = items[:10]
        extracted_count = 0
        for item in items_to_extract:
            try:
                entities = entity_extractor.extract_entities(item.title, item.summary_short or "")
                entity_extractor.save_entities(db, item.id, entities)
                extracted_count += 1
            except Exception as e:
                print(f"[Full Pipeline E2E] Error extracting entities from item {item.id}: {e}")
        db.commit()
        test_results["pipeline_steps"]["entity_extraction"]["items_processed"] = extracted_count
        test_results["pipeline_steps"]["entity_extraction"]["status"] = "completed"
        print(f"[Full Pipeline E2E] Extracted entities from {extracted_count} items")

        # Step 6: Grouping (incremental mode)
        print("[Full Pipeline E2E] Step 6: Running grouping...")
        deduplicator = Deduplicator(db)
        items_to_group = [item for item in items if not item.dup_group_id][:20]
        grouped_count = 0
        for item in items_to_group:
            try:
                group_id = deduplicator.process_new_item(item)
                if group_id:
                    grouped_count += 1
            except Exception as e:
                print(f"[Full Pipeline E2E] Error grouping item {item.id}: {e}")
        db.commit()
        test_results["pipeline_steps"]["grouping"]["groups_created"] = grouped_count
        test_results["pipeline_steps"]["grouping"]["status"] = "completed"
        print(f"[Full Pipeline E2E] Grouped {grouped_count} items")

        # Step 7: Person Tracking
        print("[Full Pipeline E2E] Step 7: Running person tracking...")
        person_tracker = PersonTracker(db)
        items_to_track = items[:20]
        matches_count = 0
        for item in items_to_track:
            try:
                matched_persons = person_tracker.match_item(item)
                if matched_persons:
                    matches_count += len(matched_persons)
            except Exception as e:
                print(f"[Full Pipeline E2E] Error tracking item {item.id}: {e}")
        db.commit()
        test_results["pipeline_steps"]["person_tracking"]["matches_found"] = matches_count
        test_results["pipeline_steps"]["person_tracking"]["status"] = "completed"
        print(f"[Full Pipeline E2E] Found {matches_count} person matches")

        # Step 8: API Verification
        print("[Full Pipeline E2E] Step 8: Verifying API endpoints...")
        endpoints_tested = 0
        
        # Items API
        response = client.get("/api/items?page=1&page_size=10")
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert len(data["items"]) > 0
        endpoints_tested += 1
        
        # Groups API
        since_date = (datetime.now(timezone.utc) - timedelta(days=21)).date().isoformat()
        response = client.get(f"/api/groups?since={since_date}&page=1&page_size=10")
        assert response.status_code == 200
        data = response.json()
        assert "groups" in data
        endpoints_tested += 1
        
        # Persons API
        response = client.get("/api/persons")
        assert response.status_code == 200
        endpoints_tested += 1
        
        # Sources API
        response = client.get("/api/sources")
        assert response.status_code == 200
        endpoints_tested += 1
        
        # Constants API
        response = client.get("/api/constants/fields")
        assert response.status_code == 200
        endpoints_tested += 1
        
        response = client.get("/api/constants/custom-tags")
        assert response.status_code == 200
        endpoints_tested += 1
        
        test_results["pipeline_steps"]["api_verification"]["endpoints_tested"] = endpoints_tested
        test_results["pipeline_steps"]["api_verification"]["status"] = "completed"
        print(f"[Full Pipeline E2E] Tested {endpoints_tested} API endpoints")

        # Summary
        test_results["status"] = "passed"
        test_results["summary"] = {
            "total_items": len(items),
            "items_summarized": summarized_count,
            "items_classified": classified_count,
            "items_with_entities": extracted_count,
            "items_grouped": grouped_count,
            "person_matches": matches_count,
            "api_endpoints_tested": endpoints_tested,
        }

    except Exception as e:
        test_results["status"] = "error"
        test_results["error"] = str(e)
        import traceback
        test_results["traceback"] = traceback.format_exc()
        raise
    finally:
        # Save results
        with open(result_file, "w", encoding="utf-8") as f:
            json.dump(test_results, f, indent=2, ensure_ascii=False, default=str)
        db.close()
        print(f"\n[Full Pipeline E2E] Results saved to: {result_file}")
        print(f"[Full Pipeline E2E] Status: {test_results['status']}")
        if test_results.get("summary"):
            print(f"[Full Pipeline E2E] Summary: {json.dumps(test_results['summary'], indent=2)}")

