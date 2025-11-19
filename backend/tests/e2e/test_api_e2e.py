"""E2E tests for all API endpoints using real database data."""

from datetime import datetime, timezone, timedelta, date
from pathlib import Path
import json
import pytest

from fastapi.testclient import TestClient

from backend.app.main import app
from backend.app.core.database import SessionLocal
from backend.app.core.constants import PRD_RSS_SOURCES
from backend.app.services.rss_collector import RSSCollector
from backend.app.models.source import Source
from backend.app.models.item import Item
from backend.app.models.person import Person
from backend.app.models.bookmark import Bookmark
from backend.app.models.watch_rule import WatchRule


@pytest.mark.slow
@pytest.mark.e2e_real_data
def test_api_e2e_full_flow():
    """E2E test for all API endpoints with real database data."""
    client = TestClient(app)
    db = SessionLocal()
    results_dir = Path(__file__).parent.parent / "results"
    results_dir.mkdir(exist_ok=True)
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    result_file = results_dir / f"api_e2e_full_flow_{timestamp}.json"

    test_results = {
        "test_name": "test_api_e2e_full_flow",
        "timestamp": timestamp,
        "data_preparation": {
            "sources_created": 0,
            "items_collected": 0,
            "items_in_db": 0,
            "status": "running",
        },
        "api_tests": {
            "items": {},
            "sources": {},
            "persons": {},
            "bookmarks": {},
            "watch_rules": {},
            "insights": {},
        },
        "status": "running",
    }

    try:
        # Step 1: Ensure sources exist (PRD_RSS_SOURCES)
        sources_created = 0
        for source_data in PRD_RSS_SOURCES:
            source = db.query(Source).filter(Source.feed_url == source_data["feed_url"]).first()
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
        test_results["data_preparation"]["sources_created"] = sources_created

        # Step 2: Get existing items from DB
        items = db.query(Item).order_by(Item.published_at.desc()).limit(100).all()
        test_results["data_preparation"]["items_in_db"] = len(items)

        # Step 3: If no items, collect from active sources
        if len(items) == 0:
            print("[API E2E] No items in DB, collecting from active sources...")
            collector = RSSCollector(db)
            active_sources = db.query(Source).filter(Source.is_active == True).all()
            total_collected = 0
            for source in active_sources:
                try:
                    count = collector.collect_source(source)
                    total_collected += count
                except Exception as e:
                    print(f"[API E2E] Error collecting from {source.title}: {e}")
            test_results["data_preparation"]["items_collected"] = total_collected
            items = db.query(Item).order_by(Item.published_at.desc()).limit(100).all()

        # Final assertion: must have items
        assert (
            len(items) > 0
        ), "E2E 테스트는 반드시 아이템이 있어야 함. 소스 등록 및 RSS 수집을 먼저 실행하세요."
        test_results["data_preparation"]["status"] = "completed"

        # Step 4: Test Items API
        print("[API E2E] Testing Items API...")
        items_test = {}

        # GET /api/items
        response = client.get("/api/items?page=1&page_size=10")
        items_test["list"] = {
            "status_code": response.status_code,
            "has_items": False,
            "total": 0,
            "page": 0,
            "page_size": 0,
        }
        if response.status_code == 200:
            data = response.json()
            items_test["list"]["has_items"] = len(data.get("items", [])) > 0
            items_test["list"]["total"] = data.get("total", 0)
            items_test["list"]["page"] = data.get("page", 0)
            items_test["list"]["page_size"] = data.get("page_size", 0)

        # GET /api/items/{id}
        if items:
            item_id = items[0].id
            response = client.get(f"/api/items/{item_id}")
            items_test["detail"] = {
                "status_code": response.status_code,
                "item_id": item_id,
                "has_data": False,
            }
            if response.status_code == 200:
                data = response.json()
                items_test["detail"]["has_data"] = data.get("id") == item_id

        # GET /api/items with filters
        response = client.get("/api/items?custom_tag=agents&page=1&page_size=5")
        items_test["filter_custom_tag"] = {"status_code": response.status_code, "filtered_count": 0}
        if response.status_code == 200:
            data = response.json()
            items_test["filter_custom_tag"]["filtered_count"] = len(data.get("items", []))

        # GET /api/items/group/{dup_group_id}
        items_with_group = db.query(Item).filter(Item.dup_group_id.isnot(None)).limit(1).all()
        if items_with_group:
            dup_group_id = items_with_group[0].dup_group_id
            response = client.get(f"/api/items/group/{dup_group_id}")
            items_test["group"] = {
                "status_code": response.status_code,
                "dup_group_id": dup_group_id,
                "items_count": 0,
            }
            if response.status_code == 200:
                data = response.json()
                items_test["group"]["items_count"] = len(data) if isinstance(data, list) else 0

        test_results["api_tests"]["items"] = items_test

        # Step 5: Test Sources API
        print("[API E2E] Testing Sources API...")
        sources_test = {}

        # GET /api/sources
        response = client.get("/api/sources")
        sources_test["list"] = {"status_code": response.status_code, "count": 0}
        if response.status_code == 200:
            data = response.json()
            sources_test["list"]["count"] = len(data) if isinstance(data, list) else 0

        # GET /api/sources/{id}
        sources = db.query(Source).limit(1).all()
        if sources:
            source_id = sources[0].id
            response = client.get(f"/api/sources/{source_id}")
            sources_test["detail"] = {
                "status_code": response.status_code,
                "source_id": source_id,
                "has_data": False,
            }
            if response.status_code == 200:
                data = response.json()
                sources_test["detail"]["has_data"] = data.get("id") == source_id

        test_results["api_tests"]["sources"] = sources_test

        # Step 6: Test Persons API
        print("[API E2E] Testing Persons API...")
        persons_test = {}

        # GET /api/persons
        response = client.get("/api/persons")
        persons_test["list"] = {"status_code": response.status_code, "count": 0}
        if response.status_code == 200:
            data = response.json()
            persons_test["list"]["count"] = len(data) if isinstance(data, list) else 0

        # GET /api/persons/{id} with timeline and graph
        persons = db.query(Person).limit(1).all()
        if persons:
            person_id = persons[0].id
            response = client.get(
                f"/api/persons/{person_id}?include_timeline=true&include_graph=true"
            )
            persons_test["detail"] = {
                "status_code": response.status_code,
                "person_id": person_id,
                "has_timeline": False,
                "has_graph": False,
            }
            if response.status_code == 200:
                data = response.json()
                persons_test["detail"]["has_timeline"] = len(data.get("timeline", [])) > 0
                persons_test["detail"]["has_graph"] = data.get("relationship_graph") is not None

        test_results["api_tests"]["persons"] = persons_test

        # Step 7: Test Bookmarks API
        print("[API E2E] Testing Bookmarks API...")
        bookmarks_test = {}

        # GET /api/bookmarks
        response = client.get("/api/bookmarks")
        bookmarks_test["list"] = {"status_code": response.status_code, "count": 0}
        if response.status_code == 200:
            data = response.json()
            bookmarks_test["list"]["count"] = len(data) if isinstance(data, list) else 0

        # POST /api/bookmarks (create a test bookmark)
        if items:
            test_item = items[0]
            bookmark_data = {
                "item_id": test_item.id,
                "title": f"Test Bookmark {timestamp}",
                "tags": ["test", "e2e"],
                "note": "E2E test bookmark",
            }
            response = client.post("/api/bookmarks", json=bookmark_data)
            bookmarks_test["create"] = {"status_code": response.status_code, "bookmark_id": None}
            if response.status_code == 201:
                data = response.json()
                bookmarks_test["create"]["bookmark_id"] = data.get("id")

                # DELETE /api/bookmarks/{id}
                bookmark_id = data.get("id")
                response = client.delete(f"/api/bookmarks/{bookmark_id}")
                bookmarks_test["delete"] = {
                    "status_code": response.status_code,
                    "bookmark_id": bookmark_id,
                }

        test_results["api_tests"]["bookmarks"] = bookmarks_test

        # Step 8: Test Watch Rules API
        print("[API E2E] Testing Watch Rules API...")
        watch_rules_test = {}

        # GET /api/watch-rules
        response = client.get("/api/watch-rules")
        watch_rules_test["list"] = {"status_code": response.status_code, "count": 0}
        if response.status_code == 200:
            data = response.json()
            watch_rules_test["list"]["count"] = len(data) if isinstance(data, list) else 0

        # GET /api/watch-rules/{id}
        rules = db.query(WatchRule).limit(1).all()
        if rules:
            rule_id = rules[0].id
            response = client.get(f"/api/watch-rules/{rule_id}")
            watch_rules_test["detail"] = {
                "status_code": response.status_code,
                "rule_id": rule_id,
                "has_data": False,
            }
            if response.status_code == 200:
                data = response.json()
                watch_rules_test["detail"]["has_data"] = data.get("id") == rule_id

        test_results["api_tests"]["watch_rules"] = watch_rules_test

        # Step 9: Test Insights API
        print("[API E2E] Testing Insights API...")
        insights_test = {}

        # GET /api/insights/weekly
        response = client.get("/api/insights/weekly?days=7")
        insights_test["weekly"] = {
            "status_code": response.status_code,
            "has_keywords": False,
            "has_person_insights": False,
        }
        if response.status_code == 200:
            data = response.json()
            insights_test["weekly"]["has_keywords"] = len(data.get("top_keywords", [])) > 0
            insights_test["weekly"]["has_person_insights"] = (
                len(data.get("person_insights", [])) > 0
            )

        # GET /api/insights/keywords
        response = client.get("/api/insights/keywords?days=7")
        insights_test["keywords"] = {"status_code": response.status_code, "trends_count": 0}
        if response.status_code == 200:
            data = response.json()
            insights_test["keywords"]["trends_count"] = len(data) if isinstance(data, list) else 0

        # GET /api/insights/persons/{person_id}
        if persons:
            person_id = persons[0].id
            response = client.get(f"/api/insights/persons/{person_id}?days=7")
            insights_test["person"] = {
                "status_code": response.status_code,
                "person_id": person_id,
                "has_events": False,
            }
            if response.status_code == 200:
                data = response.json()
                insights_test["person"]["has_events"] = len(data.get("recent_events", [])) > 0

        test_results["api_tests"]["insights"] = insights_test

        # Summary
        test_results["status"] = "passed"
        test_results["summary"] = {
            "total_endpoints_tested": 6,
            "items_api": items_test.get("list", {}).get("status_code") == 200,
            "sources_api": sources_test.get("list", {}).get("status_code") == 200,
            "persons_api": persons_test.get("list", {}).get("status_code") == 200,
            "bookmarks_api": bookmarks_test.get("list", {}).get("status_code") == 200,
            "watch_rules_api": watch_rules_test.get("list", {}).get("status_code") == 200,
            "insights_api": insights_test.get("weekly", {}).get("status_code") == 200,
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
        print(f"\n[API E2E TEST RESULTS] Saved to: {result_file}")
        print(f"[API E2E TEST RESULTS] Status: {test_results['status']}")
        if test_results.get("summary"):
            print(
                f"[API E2E TEST RESULTS] Summary: {json.dumps(test_results['summary'], indent=2)}"
            )
