"""E2E test for PersonTracker using real RSS data.

Behavior:
- Creates initial 5 persons with watch rules (Yann LeCun, Andrej Karpathy, etc.)
- Collects real RSS items from multiple sources
- Matches items to persons using watch rules
- Saves detailed results to backend/tests/results/*.json
- Skips gracefully if no new items are collected or network is unavailable.
"""

import json
import sys
import io
from pathlib import Path
from datetime import datetime, timezone, timedelta, date

# Fix Windows PowerShell encoding
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8")

import pytest

from backend.app.services.rss_collector import RSSCollector
from backend.app.services.person_tracker import PersonTracker
from backend.app.models.source import Source
from backend.app.models.item import Item
from backend.app.models.person import Person
from backend.app.models.watch_rule import WatchRule
from backend.app.models.person_timeline import PersonTimeline
from backend.app.core.database import SessionLocal
from backend.app.core.config import get_settings
from backend.app.core.constants import PRD_RSS_SOURCES
from sqlalchemy import func, inspect


# Initial 5 persons and their watch rules
INITIAL_PERSONS = [
    {
        "name": "Yann LeCun",
        "bio": "Chief AI Scientist at Meta",
        "rules": [
            {
                "label": "JEPA variants",
                "include_rules": ["JEPA", "I-JEPA", "V-JEPA", "Meta", "LeCun"],  # 하위 호환
                "required_keywords": [],  # 필수 키워드 없음
                "optional_keywords": ["JEPA", "I-JEPA", "V-JEPA", "Meta", "LeCun"],  # OR 조건
                "exclude_rules": [],
                "priority": 10,
            }
        ],
    },
    {
        "name": "Andrej Karpathy",
        "bio": "Former Director of AI at Tesla, Founder of Eureka Labs",
        "rules": [
            {
                "label": "NanoChat and Eureka Labs",
                "include_rules": ["NanoChat", "Eureka Labs", "LLM101n", "Karpathy"],  # 하위 호환
                "required_keywords": [],
                "optional_keywords": ["NanoChat", "Eureka Labs", "LLM101n", "Karpathy"],
                "exclude_rules": [],
                "priority": 10,
            }
        ],
    },
    {
        "name": "David Luan",
        "bio": "Co-founder of Adept AI, Former VP of Engineering at OpenAI",
        "rules": [
            {
                "label": "Agentic and Amazon Nova",
                "include_rules": ["agentic", "Amazon Nova", "AGI SF Lab", "David Luan"],  # 하위 호환
                "required_keywords": [],  # 필수 키워드 없음
                "optional_keywords": ["Amazon Nova", "AGI SF Lab", "David Luan", "Adept AI"],  # "agentic" 제거 (너무 일반적)
                "exclude_rules": [],
                "priority": 10,
            }
        ],
    },
    {
        "name": "Llion Jones",
        "bio": "Co-founder of Sakana AI, Former Research Scientist at Google",
        "rules": [
            {
                "label": "Sakana AI models",
                "include_rules": ["Sakana AI", "Sakana"],  # 하위 호환
                "required_keywords": [],
                "optional_keywords": ["Sakana AI", "Sakana"],
                "exclude_rules": [],
                "priority": 10,
            },
            {
                "label": "Sakana AI papers/benchmarks",
                "include_rules": ["Sakana", "model", "paper", "benchmark"],  # 하위 호환 (기존 규칙 유지)
                "required_keywords": ["Sakana"],  # 필수: "Sakana" 반드시 포함 (AND)
                "optional_keywords": ["paper", "benchmark"],  # 선택: "model" 제거 (너무 일반적)
                "exclude_rules": ["arxiv", "arXiv"],  # arXiv 제외
                "priority": 5,
            },
        ],
    },
    {
        "name": "AUI/Apollo-1",
        "bio": "Neuro-symbolic AI system",
        "rules": [
            {
                "label": "Apollo-1 and neuro-symbolic",
                "include_rules": ["Apollo-1", "neuro-symbolic", "stateful reasoning"],  # 하위 호환
                "required_keywords": [],
                "optional_keywords": ["Apollo-1", "neuro-symbolic", "stateful reasoning"],
                "exclude_rules": [],
                "priority": 10,
            }
        ],
    },
]


@pytest.mark.slow
@pytest.mark.e2e_real_data
def test_person_tracker_e2e_real_data():
    """E2E test: Create initial persons, collect RSS items, and match them."""
    db = SessionLocal()
    results_dir = Path(__file__).parent.parent / "results"
    results_dir.mkdir(exist_ok=True)
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    result_file = results_dir / f"person_tracker_e2e_real_data_{timestamp}.json"

    # Calculate 21-day window (same as Phase 1.3)
    ref_date = date.today()
    start_dt = datetime(ref_date.year, ref_date.month, ref_date.day, tzinfo=timezone.utc) - timedelta(days=21)
    end_dt = datetime(ref_date.year, ref_date.month, ref_date.day, tzinfo=timezone.utc)

    test_results = {
        "test_name": "test_person_tracker_e2e_real_data",
        "timestamp": timestamp,
        "window": {
            "start": start_dt.isoformat(),
            "end": end_dt.isoformat(),
            "days": 21
        },
        "persons_created": [],
        "collection": {"sources": [], "total_items": 0, "items_in_window": 0},
        "matching": {
            "total_items": 0,
            "items_in_window": 0,
            "matched_items": 0,
            "total_matches": 0,
            "matches_by_person": {},
        },
        "timeline_events": [],
        "status": "running",
    }

    try:
        # Step 0: Verify database connection and check items
        print("[PersonTracker E2E] ===== Database Connection Verification =====")
        settings = get_settings()
        db_url = settings.DATABASE_URL

        # Mask password in URL for logging
        if "@" in db_url:
            parts = db_url.split("@")
            if len(parts) == 2:
                masked_url = f"{parts[0].split('://')[0]}://***:***@{parts[1]}"
            else:
                masked_url = "***MASKED***"
        else:
            masked_url = db_url

        print(f"[PersonTracker E2E] DATABASE_URL: {masked_url}")
        test_results["database_url_masked"] = masked_url

        # Check database tables
        try:
            inspector = inspect(db.bind)
            tables = inspector.get_table_names()
            print(f"[PersonTracker E2E] Database tables: {len(tables)} found")
            print(f"  Tables: {', '.join(sorted(tables))}")
            test_results["database_tables"] = sorted(tables)
            test_results["has_items_table"] = "items" in tables
        except Exception as e:
            print(f"[PersonTracker E2E] Failed to inspect tables: {e}")
            test_results["inspect_error"] = str(e)

        # Check Item table and get statistics
        print(f"[PersonTracker E2E] ===== Item Table Statistics =====")
        try:
            total_items = db.query(Item).count()
            print(f"[PersonTracker E2E] Total items: {total_items}")
            test_results["total_items_in_db"] = total_items

            # Source-wise statistics
            source_stats = (
                db.query(
                    Source.id,
                    Source.title,
                    Source.feed_url,
                    func.count(Item.id).label("item_count"),
                )
                .outerjoin(Item, Source.id == Item.source_id)
                .group_by(Source.id, Source.title, Source.feed_url)
                .order_by(func.count(Item.id).desc())
                .all()
            )

            print(f"[PersonTracker E2E] Source-wise item counts:")
            source_summary = []
            for stat in source_stats:
                print(f"  [{stat.item_count:4d}] Source ID {stat.id}: {stat.title}")
                source_summary.append(
                    {
                        "source_id": stat.id,
                        "title": stat.title,
                        "feed_url": stat.feed_url,
                        "item_count": stat.item_count,
                    }
                )
            test_results["source_statistics"] = source_summary

            # Sample items
            if total_items > 0:
                sample_items = db.query(Item).order_by(Item.published_at.desc()).limit(3).all()
                print(f"[PersonTracker E2E] Sample items (latest 3):")
                for item in sample_items:
                    print(f"  Item {item.id}: {item.title[:70]}...")
                    print(f"    Published: {item.published_at}, Source ID: {item.source_id}")
            else:
                print(f"[PersonTracker E2E] No items found in database!")
                print(f"[PersonTracker E2E] Possible causes:")
                print(f"  1. Database is empty (no RSS collection has been run)")
                print(f"  2. Connected to wrong database (check DATABASE_URL)")
                print(f"  3. Items table exists but is empty")

        except Exception as e:
            print(f"[PersonTracker E2E] Error querying items: {e}")
            import traceback

            test_results["query_error"] = str(e)
            test_results["query_traceback"] = traceback.format_exc()

        print(f"[PersonTracker E2E] ===== End Database Verification =====")
        print()

        # Step 1: Create initial persons and watch rules
        print("[PersonTracker E2E] Creating initial persons and watch rules...")
        persons_dict = {}

        for person_data in INITIAL_PERSONS:
            # Check if person already exists
            existing = db.query(Person).filter(Person.name == person_data["name"]).first()
            if existing:
                person = existing
                print(f"[PersonTracker E2E] Person already exists: {person.name} (ID: {person.id})")
            else:
                person = Person(name=person_data["name"], bio=person_data.get("bio"))
                db.add(person)
                db.flush()
                print(f"[PersonTracker E2E] Created person: {person.name} (ID: {person.id})")

            persons_dict[person.name] = person

            # Create watch rules
            rules_created = []
            for rule_data in person_data["rules"]:
                # Check if rule already exists
                existing_rule = (
                    db.query(WatchRule)
                    .filter(WatchRule.person_id == person.id, WatchRule.label == rule_data["label"])
                    .first()
                )

                if existing_rule:
                    # 기존 규칙 업데이트 (required_keywords, optional_keywords 추가)
                    existing_rule.required_keywords = rule_data.get("required_keywords", [])
                    existing_rule.optional_keywords = rule_data.get("optional_keywords", [])
                    existing_rule.include_rules = rule_data.get("include_rules", [])
                    existing_rule.exclude_rules = rule_data.get("exclude_rules", [])
                    existing_rule.priority = rule_data.get("priority", 0)
                    rule = existing_rule
                    db.commit()
                    print(f"[PersonTracker E2E] Rule updated: {rule.label} (ID: {rule.id})")
                else:
                    rule = WatchRule(
                        label=rule_data["label"],
                        include_rules=rule_data.get("include_rules", []),
                        exclude_rules=rule_data.get("exclude_rules", []),
                        required_keywords=rule_data.get("required_keywords", []),
                        optional_keywords=rule_data.get("optional_keywords", []),
                        priority=rule_data.get("priority", 0),
                        person_id=person.id,
                    )
                    db.add(rule)
                    db.flush()
                    print(f"[PersonTracker E2E] Created rule: {rule.label} (ID: {rule.id})")

                rules_created.append(
                    {
                        "id": rule.id,
                        "label": rule.label,
                        "include_rules": rule.include_rules,
                        "exclude_rules": rule.exclude_rules,
                        "required_keywords": rule.required_keywords,
                        "optional_keywords": rule.optional_keywords,
                        "priority": rule.priority,
                    }
                )

            test_results["persons_created"].append(
                {"id": person.id, "name": person.name, "bio": person.bio, "rules": rules_created}
            )

        db.commit()
        print(f"[PersonTracker E2E] Created {len(persons_dict)} persons with watch rules")

        # Step 1.5: Ensure sources exist (PRD_RSS_SOURCES)
        print("[PersonTracker E2E] Ensuring RSS sources exist...")
        for source_data in PRD_RSS_SOURCES:
            source = db.query(Source).filter(
                Source.feed_url == source_data["feed_url"]
            ).first()
            if not source:
                source = Source(**source_data, is_active=True)
                db.add(source)
                print(f"[PersonTracker E2E] Created source: {source.title} ({source.feed_url})")
            elif not source.is_active:
                source.is_active = True
                print(f"[PersonTracker E2E] Activated source: {source.title}")
        db.commit()

        # Step 2: Get existing items first (before collection)
        print("[PersonTracker E2E] Getting existing items from database...")
        all_items = db.query(Item).order_by(Item.published_at.desc()).all()
        print(f"[PersonTracker E2E] Found {len(all_items)} existing items in database")

        # Helper function to make datetime timezone-aware if needed
        def make_aware(dt):
            if dt is None:
                return None
            if dt.tzinfo is None:
                # Assume UTC if timezone-naive
                return dt.replace(tzinfo=timezone.utc)
            return dt

        # Filter items within 21-day window
        print(f"[PersonTracker E2E] Filtering items within 21-day window ({start_dt.date()} to {end_dt.date()})...")
        items_in_window = []
        for item in all_items:
            if item.published_at:
                item_dt = make_aware(item.published_at)
                if start_dt <= item_dt <= end_dt:
                    items_in_window.append(item)

        print(f"[PersonTracker E2E] Items in 21-day window: {len(items_in_window)}")

        # Step 2.5: Collect RSS items only if no items in window and no items at all
        if len(items_in_window) == 0 and len(all_items) == 0:
            print(f"[PersonTracker E2E] No items found, collecting RSS items from active sources (21-day window: {start_dt.date()} to {end_dt.date()})...")
            collector = RSSCollector(db)
            active_sources = db.query(Source).filter(Source.is_active == True).all()
            print(f"[PersonTracker E2E] Found {len(active_sources)} active sources")
            
            collection_results = []
            total_collected = 0
            
            for source in active_sources:
                try:
                    count = collector.collect_source(source)
                    total_collected += count
                    collection_results.append({
                        "source_id": source.id,
                        "source_title": source.title,
                        "feed_url": source.feed_url,
                        "count": count,
                        "status": "success"
                    })
                    print(f"[PersonTracker E2E] Collected {count} items from {source.title}")
                except Exception as e:
                    collection_results.append({
                        "source_id": source.id,
                        "source_title": source.title,
                        "feed_url": source.feed_url,
                        "count": 0,
                        "status": "error",
                        "error": str(e)
                    })
                    print(f"[PersonTracker E2E] Error collecting from {source.title}: {e}")
            
            test_results["collection"]["sources"] = collection_results
            test_results["collection"]["total_items"] = total_collected
            print(f"[PersonTracker E2E] Total collected: {total_collected} items from {len(active_sources)} sources")
            
            # Re-query items after collection
            all_items = db.query(Item).order_by(Item.published_at.desc()).all()
            items_in_window = []
            for item in all_items:
                if item.published_at:
                    item_dt = make_aware(item.published_at)
                    if start_dt <= item_dt <= end_dt:
                        items_in_window.append(item)
        else:
            print("[PersonTracker E2E] Using existing items from database (skipping collection)")
            test_results["collection"]["sources"] = []
            test_results["collection"]["total_items"] = 0

        # Step 3: Use items in window for matching (or all items if window is empty)
        items = items_in_window if items_in_window else all_items
        print(f"[PersonTracker E2E] Processing {len(items)} items for matching")

        test_results["collection"]["items_in_window"] = len(items_in_window)
        test_results["matching"]["total_items"] = len(all_items)
        test_results["matching"]["items_in_window"] = len(items_in_window)

        if len(items) == 0:
            print("[PersonTracker E2E] Error: No items in database (neither in window nor total)!")
            print("[PersonTracker E2E] This test requires at least some items to match against persons")
            print("[PersonTracker E2E] E2E 테스트는 반드시 아이템이 있어야 함. 소스 등록 및 RSS 수집을 먼저 실행하세요.")
            test_results["status"] = "error"
            test_results["error"] = "No items in database after RSS collection. E2E 테스트는 반드시 아이템이 있어야 함. 소스 등록 및 RSS 수집을 먼저 실행하세요."
            return

        # Step 4: Match items to persons
        print("[PersonTracker E2E] Matching items to persons...")
        tracker = PersonTracker(db)

        matched_items_count = 0
        total_matches = 0
        matches_by_person = {name: 0 for name in persons_dict.keys()}
        matched_items_detail = []
        keyword_statistics = {}  # 키워드별 통계

        for item in items:
            matched_results = tracker.match_item(item)  # Dict 리스트 반환
            if matched_results:
                matched_items_count += 1
                total_matches += len(matched_results)
                
                matched_person_info = []
                for result in matched_results:
                    person = result["person"]
                    matched_keywords = result["matched_keywords"]
                    rule_label = result["rule_label"]
                    
                    matches_by_person[person.name] = matches_by_person.get(person.name, 0) + 1
                    
                    # 키워드 통계
                    for keyword in matched_keywords:
                        keyword_statistics[keyword] = keyword_statistics.get(keyword, 0) + 1
                    
                    matched_person_info.append({
                        "person_name": person.name,
                        "person_id": person.id,
                        "matched_keywords": matched_keywords,
                        "rule_label": rule_label
                    })
                
                matched_items_detail.append({
                    "item_id": item.id,
                    "item_title": item.title[:100] if item.title else None,
                    "published_at": item.published_at.isoformat() if item.published_at else None,
                    "source_id": item.source_id,
                    "matched_persons": matched_person_info
                })

        test_results["matching"]["matched_items"] = matched_items_count
        test_results["matching"]["total_matches"] = total_matches
        test_results["matching"]["matches_by_person"] = matches_by_person
        test_results["matching"]["matched_items_detail"] = matched_items_detail[:50]  # Limit to first 50 for readability
        test_results["matching"]["keyword_statistics"] = dict(sorted(keyword_statistics.items(), key=lambda x: x[1], reverse=True))

        print(
            f"[PersonTracker E2E] Matched {matched_items_count} items to {total_matches} person(s)"
        )
        print(f"[PersonTracker E2E] Matches by person: {matches_by_person}")
        print(f"[PersonTracker E2E] Top matched keywords: {dict(list(test_results['matching']['keyword_statistics'].items())[:10])}")

        # Step 5: Get timeline events for all persons
        print("[PersonTracker E2E] Retrieving timeline events...")
        for person_name, person in persons_dict.items():
            events = (
                db.query(PersonTimeline)
                .filter(PersonTimeline.person_id == person.id)
                .order_by(PersonTimeline.created_at.desc())
                .limit(10)
                .all()
            )

            for event in events:
                item = db.query(Item).filter(Item.id == event.item_id).first()
                test_results["timeline_events"].append(
                    {
                        "person_id": person.id,
                        "person_name": person.name,
                        "item_id": event.item_id,
                        "item_title": item.title if item else None,
                        "event_type": event.event_type,
                        "description": event.description,
                        "created_at": event.created_at.isoformat() if event.created_at else None,
                    }
                )

        test_results["status"] = "success"
        print(f"[PersonTracker E2E] Test completed successfully")

    except Exception as e:
        test_results["status"] = "error"
        test_results["error"] = str(e)
        print(f"[PersonTracker E2E] Test failed: {e}")
        import traceback

        test_results["traceback"] = traceback.format_exc()

    finally:
        # Save results to JSON file
        with open(result_file, "w", encoding="utf-8") as f:
            json.dump(test_results, f, indent=2, ensure_ascii=False, default=str)
        print(f"[PersonTracker E2E] Results saved to {result_file}")
        db.close()
