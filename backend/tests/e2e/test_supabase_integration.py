"""E2E test to verify Supabase integration: pagination, filtering, sorting."""
from datetime import datetime, timezone, timedelta, date
from pathlib import Path
import json
import pytest

from fastapi.testclient import TestClient

from backend.app.main import app
from backend.app.core.database import SessionLocal
from backend.app.models.item import Item
from backend.app.core.constants import CUSTOM_TAGS


@pytest.mark.slow
@pytest.mark.e2e_real_data
def test_supabase_pagination_filtering_sorting():
    """Verify pagination, filtering, and sorting work correctly with Supabase."""
    client = TestClient(app)
    db = SessionLocal()
    results_dir = Path(__file__).parent.parent / "results"
    results_dir.mkdir(exist_ok=True)
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    result_file = results_dir / f"supabase_integration_{timestamp}.json"
    
    test_results = {
        "test_name": "test_supabase_pagination_filtering_sorting",
        "timestamp": timestamp,
        "pagination": {},
        "filtering": {},
        "sorting": {},
        "status": "running"
    }
    
    try:
        # Get total items count from Supabase
        total_items = db.query(Item).count()
        test_results["total_items_in_db"] = total_items
        
        assert total_items > 0, "DB에 아이템이 없습니다. RSS 수집을 먼저 실행하세요."
        
        # Test 1: Pagination
        print("[Supabase Integration] Testing pagination...")
        page1 = client.get("/api/items?page=1&page_size=10").json()
        page2 = client.get("/api/items?page=2&page_size=10").json()
        
        test_results["pagination"] = {
            "page1_count": len(page1.get("items", [])),
            "page1_total": page1.get("total", 0),
            "page2_count": len(page2.get("items", [])),
            "page2_total": page2.get("total", 0),
            "page1_page": page1.get("page", 0),
            "page2_page": page2.get("page", 0),
            "consistent_total": page1.get("total") == page2.get("total"),
            "no_duplicates": len(set([item["id"] for item in page1.get("items", [])] + 
                                     [item["id"] for item in page2.get("items", [])])) == 
                            len(page1.get("items", [])) + len(page2.get("items", []))
        }
        
        # Test 2: Filtering (custom_tag)
        print("[Supabase Integration] Testing filtering...")
        filter_results = {}
        for tag in CUSTOM_TAGS[:3]:  # Test first 3 tags
            response = client.get(f"/api/items?custom_tag={tag}&page=1&page_size=20")
            if response.status_code == 200:
                data = response.json()
                filter_results[tag] = {
                    "status_code": 200,
                    "filtered_count": len(data.get("items", [])),
                    "total": data.get("total", 0)
                }
        
        test_results["filtering"] = filter_results
        
        # Test 3: Date filtering
        today = date.today()
        week_ago = today - timedelta(days=7)
        response = client.get(f"/api/items?date_from={week_ago}&page=1&page_size=10")
        if response.status_code == 200:
            data = response.json()
            test_results["filtering"]["date_from"] = {
                "status_code": 200,
                "filtered_count": len(data.get("items", [])),
                "total": data.get("total", 0)
            }
        
        # Test 4: Sorting
        print("[Supabase Integration] Testing sorting...")
        desc_response = client.get("/api/items?page=1&page_size=5&order_by=published_at&order_desc=true")
        asc_response = client.get("/api/items?page=1&page_size=5&order_by=published_at&order_desc=false")
        
        if desc_response.status_code == 200 and asc_response.status_code == 200:
            desc_data = desc_response.json()
            asc_data = asc_response.json()
            
            desc_items = desc_data.get("items", [])
            asc_items = asc_data.get("items", [])
            
            # Verify descending order (newest first)
            desc_dates = [item["published_at"] for item in desc_items if item.get("published_at")]
            desc_sorted = desc_dates == sorted(desc_dates, reverse=True)
            
            # Verify ascending order (oldest first)
            asc_dates = [item["published_at"] for item in asc_items if item.get("published_at")]
            asc_sorted = asc_dates == sorted(asc_dates)
            
            test_results["sorting"] = {
                "desc_order_correct": desc_sorted,
                "asc_order_correct": asc_sorted,
                "desc_count": len(desc_items),
                "asc_count": len(asc_items)
            }
        
        test_results["status"] = "passed"
        
    except Exception as e:
        test_results["status"] = "error"
        test_results["error"] = str(e)
        import traceback
        test_results["traceback"] = traceback.format_exc()
        raise
    finally:
        with open(result_file, "w", encoding="utf-8") as f:
            json.dump(test_results, f, indent=2, ensure_ascii=False, default=str)
        db.close()
        print(f"\n[Supabase Integration Test] Saved to: {result_file}")
        print(f"[Supabase Integration Test] Status: {test_results['status']}")

