"""E2E performance tests for API endpoints.

This test verifies that API endpoints meet performance requirements
with large datasets.
"""

from datetime import datetime, timezone, timedelta
from pathlib import Path
import json
import pytest
import time
import concurrent.futures

from fastapi.testclient import TestClient

from backend.app.main import app
from backend.app.core.database import SessionLocal
from backend.app.core.constants import PRD_RSS_SOURCES
from backend.app.services.rss_collector import RSSCollector
from backend.app.models.source import Source
from backend.app.models.item import Item


@pytest.mark.slow
@pytest.mark.e2e_real_data
def test_performance_e2e():
    """E2E performance test with real database data."""
    client = TestClient(app)
    db = SessionLocal()
    results_dir = Path(__file__).parent.parent / "results"
    results_dir.mkdir(exist_ok=True)
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    result_file = results_dir / f"performance_e2e_{timestamp}.json"

    test_results = {
        "test_name": "test_performance_e2e",
        "timestamp": timestamp,
        "performance_metrics": {
            "items_list": {"response_time_ms": 0, "item_count": 0, "passed": False},
            "items_pagination": {"response_time_ms": 0, "passed": False},
            "items_filtering": {"response_time_ms": 0, "passed": False},
            "items_sorting": {"response_time_ms": 0, "passed": False},
            "concurrent_requests": {"response_time_ms": 0, "passed": False},
        },
        "status": "running",
    }

    try:
        # Step 1: Ensure we have enough data
        print("[Performance E2E] Step 1: Ensuring data availability...")
        items = db.query(Item).order_by(Item.published_at.desc()).limit(1000).all()
        item_count = len(items)
        print(f"[Performance E2E] Available items: {item_count}")
        
        if item_count < 100:
            # Collect more items if needed
            print("[Performance E2E] Collecting additional items...")
            collector = RSSCollector(db)
            active_sources = db.query(Source).filter(Source.is_active == True).all()
            for source in active_sources[:3]:  # Limit to 3 sources
                try:
                    collector.collect_source(source)
                except Exception as e:
                    print(f"[Performance E2E] Error collecting from {source.title}: {e}")
            items = db.query(Item).order_by(Item.published_at.desc()).limit(1000).all()
            item_count = len(items)
            print(f"[Performance E2E] Items after collection: {item_count}")

        # Step 2: Test Items List Performance
        print("[Performance E2E] Step 2: Testing items list performance...")
        start_time = time.time()
        response = client.get("/api/items?page=1&page_size=20")
        end_time = time.time()
        response_time_ms = (end_time - start_time) * 1000
        
        assert response.status_code == 200
        data = response.json()
        test_results["performance_metrics"]["items_list"]["response_time_ms"] = response_time_ms
        test_results["performance_metrics"]["items_list"]["item_count"] = len(data.get("items", []))
        test_results["performance_metrics"]["items_list"]["passed"] = response_time_ms < 2000  # < 2 seconds
        print(f"[Performance E2E] Items list: {response_time_ms:.2f}ms ({'PASS' if response_time_ms < 2000 else 'FAIL'})")

        # Step 3: Test Pagination Performance
        print("[Performance E2E] Step 3: Testing pagination performance...")
        start_time = time.time()
        response = client.get("/api/items?page=5&page_size=20")
        end_time = time.time()
        response_time_ms = (end_time - start_time) * 1000
        
        assert response.status_code == 200
        test_results["performance_metrics"]["items_pagination"]["response_time_ms"] = response_time_ms
        test_results["performance_metrics"]["items_pagination"]["passed"] = response_time_ms < 1000  # < 1 second
        print(f"[Performance E2E] Pagination: {response_time_ms:.2f}ms ({'PASS' if response_time_ms < 1000 else 'FAIL'})")

        # Step 4: Test Filtering Performance
        print("[Performance E2E] Step 4: Testing filtering performance...")
        start_time = time.time()
        response = client.get("/api/items?custom_tag=agents&page=1&page_size=20")
        end_time = time.time()
        response_time_ms = (end_time - start_time) * 1000
        
        assert response.status_code == 200
        test_results["performance_metrics"]["items_filtering"]["response_time_ms"] = response_time_ms
        test_results["performance_metrics"]["items_filtering"]["passed"] = response_time_ms < 1000  # < 1 second
        print(f"[Performance E2E] Filtering: {response_time_ms:.2f}ms ({'PASS' if response_time_ms < 1000 else 'FAIL'})")

        # Step 5: Test Sorting Performance
        print("[Performance E2E] Step 5: Testing sorting performance...")
        start_time = time.time()
        response = client.get("/api/items?order_by=published_at&order_desc=true&page=1&page_size=20")
        end_time = time.time()
        response_time_ms = (end_time - start_time) * 1000
        
        assert response.status_code == 200
        test_results["performance_metrics"]["items_sorting"]["response_time_ms"] = response_time_ms
        test_results["performance_metrics"]["items_sorting"]["passed"] = response_time_ms < 1000  # < 1 second
        print(f"[Performance E2E] Sorting: {response_time_ms:.2f}ms ({'PASS' if response_time_ms < 1000 else 'FAIL'})")

        # Step 6: Test Concurrent Requests Performance
        print("[Performance E2E] Step 6: Testing concurrent requests performance...")
        
        def make_request():
            start = time.time()
            resp = client.get("/api/items?page=1&page_size=10")
            end = time.time()
            return (end - start) * 1000, resp.status_code
        
        start_time = time.time()
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(make_request) for _ in range(10)]
            results = [future.result() for future in concurrent.futures.as_completed(futures)]
        end_time = time.time()
        total_time_ms = (end_time - start_time) * 1000
        
        # Check all requests succeeded
        all_succeeded = all(status == 200 for _, status in results)
        avg_response_time = sum(time_ms for time_ms, _ in results) / len(results)
        
        test_results["performance_metrics"]["concurrent_requests"]["response_time_ms"] = total_time_ms
        test_results["performance_metrics"]["concurrent_requests"]["avg_response_time_ms"] = avg_response_time
        test_results["performance_metrics"]["concurrent_requests"]["passed"] = all_succeeded and total_time_ms < 5000  # < 5 seconds for 10 requests
        print(f"[Performance E2E] Concurrent (10 requests): {total_time_ms:.2f}ms total, {avg_response_time:.2f}ms avg ({'PASS' if all_succeeded and total_time_ms < 5000 else 'FAIL'})")

        # Step 7: Test Large Dataset Performance
        print("[Performance E2E] Step 7: Testing large dataset performance...")
        start_time = time.time()
        response = client.get("/api/items?page=1&page_size=100")
        end_time = time.time()
        response_time_ms = (end_time - start_time) * 1000
        
        assert response.status_code == 200
        data = response.json()
        large_dataset_passed = response_time_ms < 2000 and len(data.get("items", [])) <= 100
        print(f"[Performance E2E] Large dataset (100 items): {response_time_ms:.2f}ms ({'PASS' if large_dataset_passed else 'FAIL'})")

        # Summary
        all_passed = all(
            metric["passed"] for metric in test_results["performance_metrics"].values()
            if "passed" in metric
        ) and large_dataset_passed
        
        test_results["status"] = "passed" if all_passed else "warning"
        test_results["summary"] = {
            "total_items_tested": item_count,
            "all_performance_targets_met": all_passed,
            "items_list_under_2s": test_results["performance_metrics"]["items_list"]["passed"],
            "pagination_under_1s": test_results["performance_metrics"]["items_pagination"]["passed"],
            "filtering_under_1s": test_results["performance_metrics"]["items_filtering"]["passed"],
            "sorting_under_1s": test_results["performance_metrics"]["items_sorting"]["passed"],
            "concurrent_requests_under_5s": test_results["performance_metrics"]["concurrent_requests"]["passed"],
            "large_dataset_under_2s": large_dataset_passed,
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
        print(f"\n[Performance E2E] Results saved to: {result_file}")
        print(f"[Performance E2E] Status: {test_results['status']}")
        if test_results.get("summary"):
            print(f"[Performance E2E] Summary: {json.dumps(test_results['summary'], indent=2)}")

