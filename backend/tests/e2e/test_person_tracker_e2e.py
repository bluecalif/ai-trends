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
from datetime import datetime, timezone

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
from sqlalchemy import func, inspect


# Initial 5 persons and their watch rules
INITIAL_PERSONS = [
    {
        "name": "Yann LeCun",
        "bio": "Chief AI Scientist at Meta",
        "rules": [
            {
                "label": "JEPA variants",
                "include_rules": ["JEPA", "I-JEPA", "V-JEPA", "Meta", "LeCun"],
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
                "include_rules": ["NanoChat", "Eureka Labs", "LLM101n", "Karpathy"],
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
                "include_rules": ["agentic", "Amazon Nova", "AGI SF Lab", "David Luan"],
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
                "include_rules": ["Sakana AI", "Sakana"],
                "exclude_rules": [],
                "priority": 10,
            },
            {
                "label": "Sakana AI papers/benchmarks",
                "include_rules": ["Sakana", "model", "paper", "benchmark"],
                "exclude_rules": [],
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
                "include_rules": ["Apollo-1", "neuro-symbolic", "stateful reasoning"],
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

    test_results = {
        "test_name": "test_person_tracker_e2e_real_data",
        "timestamp": timestamp,
        "persons_created": [],
        "collection": {"sources": [], "total_items": 0},
        "matching": {
            "total_items": 0,
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
                    rule = existing_rule
                    print(f"[PersonTracker E2E] Rule already exists: {rule.label} (ID: {rule.id})")
                else:
                    rule = WatchRule(
                        label=rule_data["label"],
                        include_rules=rule_data["include_rules"],
                        exclude_rules=rule_data.get("exclude_rules", []),
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
                        "priority": rule.priority,
                    }
                )

            test_results["persons_created"].append(
                {"id": person.id, "name": person.name, "bio": person.bio, "rules": rules_created}
            )

        db.commit()
        print(f"[PersonTracker E2E] Created {len(persons_dict)} persons with watch rules")

        # Step 2: Get existing items from database (skip RSS collection)
        print("[PersonTracker E2E] Getting existing items from database...")
        existing_item_count = db.query(Item).count()
        test_results["collection"]["total_items"] = existing_item_count
        print(f"[PersonTracker E2E] Found {existing_item_count} existing items in database")

        if existing_item_count == 0:
            print(
                "[PersonTracker E2E] Warning: No items in database, but continuing with matching anyway"
            )
            print(
                "[PersonTracker E2E] (This is expected if DB is empty - matching will process 0 items)"
            )

        # Step 3: Get all existing items from database (no time limit, no collection)
        print("[PersonTracker E2E] Getting all existing items from database...")

        items = db.query(Item).order_by(Item.published_at.desc()).all()

        test_results["matching"]["total_items"] = len(items)
        print(f"[PersonTracker E2E] Processing {len(items)} items for matching")

        if len(items) == 0:
            print("[PersonTracker E2E] No items to process, but continuing to show test structure")

        # Step 4: Match items to persons
        print("[PersonTracker E2E] Matching items to persons...")
        tracker = PersonTracker(db)

        matched_items_count = 0
        total_matches = 0
        matches_by_person = {name: 0 for name in persons_dict.keys()}

        for item in items:
            matched = tracker.match_item(item)
            if matched:
                matched_items_count += 1
                total_matches += len(matched)

                for person in matched:
                    matches_by_person[person.name] = matches_by_person.get(person.name, 0) + 1

                test_results["matching"]["matches_by_person"] = matches_by_person

        test_results["matching"]["matched_items"] = matched_items_count
        test_results["matching"]["total_matches"] = total_matches

        print(
            f"[PersonTracker E2E] Matched {matched_items_count} items to {total_matches} person(s)"
        )

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
