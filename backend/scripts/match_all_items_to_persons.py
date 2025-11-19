"""Match all existing RSS items to persons using watch rules.

This script:
1. Gets all existing items from the database
2. Matches them to persons using watch rules
3. Creates timeline events for matches
4. Prints summary statistics
"""
import sys
import io
from datetime import datetime, timezone

# Fix Windows PowerShell encoding
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

from backend.app.core.database import SessionLocal
from backend.app.services.person_tracker import PersonTracker
from backend.app.models.item import Item
from backend.app.models.person import Person
from backend.app.models.person_timeline import PersonTimeline


def main():
    """Match all existing items to persons."""
    db = SessionLocal()
    
    try:
        # Get all items
        print("[MatchAllItems] Getting all items from database...")
        items = db.query(Item).order_by(Item.published_at.desc()).all()
        total_items = len(items)
        print(f"[MatchAllItems] Found {total_items} items in database")
        
        if total_items == 0:
            print("[MatchAllItems] No items found, exiting")
            return
        
        # Get all persons
        persons = db.query(Person).all()
        print(f"[MatchAllItems] Found {len(persons)} persons with watch rules")
        
        # Initialize tracker
        tracker = PersonTracker(db)
        
        # Process items in batches
        print(f"[MatchAllItems] Processing {total_items} items...")
        matched_items_count = 0
        total_matches = 0
        matches_by_person = {}
        
        # Get existing timeline events count before matching
        existing_events_count = db.query(PersonTimeline).count()
        print(f"[MatchAllItems] Existing timeline events: {existing_events_count}")
        
        # Process items
        for i, item in enumerate(items, 1):
            if i % 50 == 0:
                print(f"[MatchAllItems] Processed {i}/{total_items} items...")
            
            matched = tracker.match_item(item)
            if matched:
                matched_items_count += 1
                total_matches += len(matched)
                
                for person in matched:
                    person_name = person.name
                    matches_by_person[person_name] = matches_by_person.get(person_name, 0) + 1
        
        # Get new timeline events count
        new_events_count = db.query(PersonTimeline).count()
        new_events = new_events_count - existing_events_count
        
        # Print summary
        print("\n" + "="*60)
        print("[MatchAllItems] SUMMARY")
        print("="*60)
        print(f"Total items processed: {total_items}")
        print(f"Items matched: {matched_items_count}")
        print(f"Total matches: {total_matches}")
        print(f"New timeline events created: {new_events}")
        print(f"Total timeline events: {new_events_count}")
        print("\nMatches by person:")
        for person_name, count in sorted(matches_by_person.items(), key=lambda x: x[1], reverse=True):
            print(f"  {person_name}: {count} matches")
        
        # Show timeline events by person
        print("\nTimeline events by person:")
        for person in persons:
            events = db.query(PersonTimeline).filter(
                PersonTimeline.person_id == person.id
            ).count()
            if events > 0:
                print(f"  {person.name}: {events} events")
        
        print("\n[MatchAllItems] Matching completed successfully!")
        
    except Exception as e:
        print(f"[MatchAllItems] Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()


if __name__ == "__main__":
    main()

