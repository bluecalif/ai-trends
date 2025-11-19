"""Integration tests for PersonTracker service."""
import pytest
from datetime import datetime, timezone

from backend.app.services.person_tracker import PersonTracker
from backend.app.models.person import Person
from backend.app.models.watch_rule import WatchRule
from backend.app.models.item import Item
from backend.app.models.source import Source
from backend.app.models.person_timeline import PersonTimeline
from backend.app.models.entity import Entity, EntityType
from backend.app.models.item_entity import item_entities


def get_unique_string(prefix: str = "") -> str:
    """Generate unique string for testing."""
    import uuid
    return f"{prefix}_{uuid.uuid4().hex[:8]}"


class TestPersonTrackerIntegration:
    """Integration tests for PersonTracker with database."""
    
    def test_match_item_and_create_timeline(self, test_db):
        """Test matching item and creating timeline event."""
        unique_id = get_unique_string()
        
        # Create source and item
        source = Source(
            title=f"Test Source {unique_id}",
            feed_url=f"https://example.com/feed_{unique_id}.xml"
        )
        test_db.add(source)
        test_db.flush()
        
        item = Item(
            source_id=source.id,
            title=f"JEPA Model Research {unique_id}",
            link=f"https://example.com/article_{unique_id}",
            published_at=datetime.now(timezone.utc),
            summary_short="Meta AI research on JEPA architecture"
        )
        test_db.add(item)
        test_db.flush()
        
        # Create person and watch rule
        person = Person(name=f"Yann LeCun {unique_id}")
        test_db.add(person)
        test_db.flush()
        
        rule = WatchRule(
            label=f"JEPA Rule {unique_id}",
            include_rules=["JEPA", "Meta"],
            exclude_rules=[],
            person_id=person.id,
            priority=1
        )
        test_db.add(rule)
        test_db.commit()
        
        # Match item
        tracker = PersonTracker(test_db)
        matched_results = tracker.match_item(item)
        
        assert len(matched_results) == 1
        assert matched_results[0]["person"].id == person.id
        assert "JEPA" in matched_results[0]["matched_keywords"] or "Meta" in matched_results[0]["matched_keywords"]
        
        # Verify timeline event
        events = test_db.query(PersonTimeline).filter(
            PersonTimeline.person_id == person.id,
            PersonTimeline.item_id == item.id
        ).all()
        assert len(events) == 1
        
        event = events[0]
        assert event.person_id == person.id
        assert event.item_id == item.id
        assert event.event_type in ["paper", "research_direction"]
        assert event.description is not None
    
    def test_multiple_rules_same_person(self, test_db):
        """Test multiple watch rules for same person."""
        unique_id = get_unique_string()
        
        source = Source(
            title=f"Test Source {unique_id}",
            feed_url=f"https://example.com/feed_{unique_id}.xml"
        )
        test_db.add(source)
        test_db.flush()
        
        item = Item(
            source_id=source.id,
            title=f"JEPA and I-JEPA Research {unique_id}",
            link=f"https://example.com/article_{unique_id}",
            published_at=datetime.now(timezone.utc),
            summary_short="Meta research"
        )
        test_db.add(item)
        test_db.flush()
        
        person = Person(name=f"Test Person {unique_id}")
        test_db.add(person)
        test_db.flush()
        
        # Create two rules for same person
        rule1 = WatchRule(
            label=f"Rule 1 {unique_id}",
            include_rules=["JEPA"],
            exclude_rules=[],
            person_id=person.id,
            priority=1
        )
        rule2 = WatchRule(
            label=f"Rule 2 {unique_id}",
            include_rules=["I-JEPA"],
            exclude_rules=[],
            person_id=person.id,
            priority=2
        )
        test_db.add(rule1)
        test_db.add(rule2)
        test_db.commit()
        
        tracker = PersonTracker(test_db)
        matched_results = tracker.match_item(item)
        
        # Should match once (same person)
        assert len(matched_results) == 1
        assert matched_results[0]["person"].id == person.id
        
        # Should create only one timeline event (duplicate prevention)
        events = test_db.query(PersonTimeline).filter(
            PersonTimeline.person_id == person.id,
            PersonTimeline.item_id == item.id
        ).all()
        assert len(events) == 1
    
    def test_exclude_rule_prevents_match(self, test_db):
        """Test that exclude rules prevent matching."""
        unique_id = get_unique_string()
        
        source = Source(
            title=f"Test Source {unique_id}",
            feed_url=f"https://example.com/feed_{unique_id}.xml"
        )
        test_db.add(source)
        test_db.flush()
        
        item = Item(
            source_id=source.id,
            title=f"JEPA Old News {unique_id}",
            link=f"https://example.com/article_{unique_id}",
            published_at=datetime.now(timezone.utc),
            summary_short="This is old news about JEPA"
        )
        test_db.add(item)
        test_db.flush()
        
        person = Person(name=f"Test Person {unique_id}")
        test_db.add(person)
        test_db.flush()
        
        rule = WatchRule(
            label=f"Test Rule {unique_id}",
            include_rules=["JEPA"],
            exclude_rules=["old news"],
            person_id=person.id
        )
        test_db.add(rule)
        test_db.commit()
        
        tracker = PersonTracker(test_db)
        matched_results = tracker.match_item(item)
        
        # Should not match due to exclude rule
        assert len(matched_results) == 0
        
        # Should not create timeline event
        events = test_db.query(PersonTimeline).filter(
            PersonTimeline.person_id == person.id
        ).all()
        assert len(events) == 0
    
    def test_priority_ordering(self, test_db):
        """Test that rules are processed in priority order."""
        unique_id = get_unique_string()
        
        source = Source(
            title=f"Test Source {unique_id}",
            feed_url=f"https://example.com/feed_{unique_id}.xml"
        )
        test_db.add(source)
        test_db.flush()
        
        item = Item(
            source_id=source.id,
            title=f"AI Research {unique_id}",
            link=f"https://example.com/article_{unique_id}",
            published_at=datetime.now(timezone.utc),
            summary_short="General AI research"
        )
        test_db.add(item)
        test_db.flush()
        
        person1 = Person(name=f"Person 1 {unique_id}")
        person2 = Person(name=f"Person 2 {unique_id}")
        test_db.add(person1)
        test_db.add(person2)
        test_db.flush()
        
        # Lower priority rule (processed first)
        rule1 = WatchRule(
            label=f"Rule 1 {unique_id}",
            include_rules=["AI"],
            exclude_rules=[],
            person_id=person1.id,
            priority=1
        )
        # Higher priority rule (processed second, but should still work)
        rule2 = WatchRule(
            label=f"Rule 2 {unique_id}",
            include_rules=["AI"],
            exclude_rules=[],
            person_id=person2.id,
            priority=2
        )
        test_db.add(rule1)
        test_db.add(rule2)
        test_db.commit()
        
        tracker = PersonTracker(test_db)
        matched_results = tracker.match_item(item)
        
        # Both should match
        assert len(matched_results) == 2
        matched_ids = {r["person"].id for r in matched_results}
        assert person1.id in matched_ids
        assert person2.id in matched_ids


class TestPersonTrackerRelationshipGraph:
    """Integration tests for relationship graph building."""
    
    def test_build_relationship_graph(self, test_db):
        """Test building relationship graph for a person."""
        unique_id = get_unique_string()
        
        # Create source and items
        source = Source(
            title=f"Test Source {unique_id}",
            feed_url=f"https://example.com/feed_{unique_id}.xml"
        )
        test_db.add(source)
        test_db.flush()
        
        item1 = Item(
            source_id=source.id,
            title=f"Item 1 {unique_id}",
            link=f"https://example.com/article1_{unique_id}",
            published_at=datetime.now(timezone.utc),
            summary_short="First article"
        )
        item2 = Item(
            source_id=source.id,
            title=f"Item 2 {unique_id}",
            link=f"https://example.com/article2_{unique_id}",
            published_at=datetime.now(timezone.utc),
            summary_short="Second article"
        )
        test_db.add(item1)
        test_db.add(item2)
        test_db.flush()
        
        # Create person and timeline events
        person = Person(name=f"Test Person {unique_id}")
        test_db.add(person)
        test_db.flush()
        
        event1 = PersonTimeline(
            person_id=person.id,
            item_id=item1.id,
            event_type="paper",
            description="First event"
        )
        event2 = PersonTimeline(
            person_id=person.id,
            item_id=item2.id,
            event_type="product",
            description="Second event"
        )
        test_db.add(event1)
        test_db.add(event2)
        test_db.commit()
        
        # Create entities and link to items
        entity1 = Entity(name=f"GPT-4 {unique_id}", type=EntityType.TECHNOLOGY)
        entity2 = Entity(name=f"OpenAI {unique_id}", type=EntityType.ORGANIZATION)
        test_db.add(entity1)
        test_db.add(entity2)
        test_db.flush()
        
        # Link entities to items
        item1.entities.append(entity1)
        item2.entities.append(entity2)
        test_db.commit()
        
        # Build relationship graph
        tracker = PersonTracker(test_db)
        graph = tracker.build_relationship_graph(person.id)
        
        assert graph["person"].id == person.id
        assert len(graph["items"]) == 2
        assert len(graph["entities"]) == 2
        assert len(graph["connections"]) > 0
        
        # Check connections
        person_connections = [
            c for c in graph["connections"]
            if c["from"] == f"person_{person.id}"
        ]
        assert len(person_connections) == 2
        
        # Check entity connections
        entity_connections = [
            c for c in graph["connections"]
            if c["type"] == "contains"
        ]
        assert len(entity_connections) == 2
    
    def test_build_graph_no_timeline(self, test_db):
        """Test building graph for person with no timeline events."""
        unique_id = get_unique_string()
        
        person = Person(name=f"Test Person {unique_id}")
        test_db.add(person)
        test_db.commit()
        
        tracker = PersonTracker(test_db)
        graph = tracker.build_relationship_graph(person.id)
        
        assert graph["person"].id == person.id
        assert len(graph["items"]) == 0
        assert len(graph["entities"]) == 0
        assert len(graph["connections"]) == 0
    
    def test_build_graph_nonexistent_person(self, test_db):
        """Test building graph for nonexistent person."""
        tracker = PersonTracker(test_db)
        graph = tracker.build_relationship_graph(99999)
        
        assert graph == {}


class TestPersonTrackerBatchProcessing:
    """Integration tests for batch item processing."""
    
    def test_process_new_items(self, test_db):
        """Test processing multiple items in batch."""
        unique_id = get_unique_string()
        
        source = Source(
            title=f"Test Source {unique_id}",
            feed_url=f"https://example.com/feed_{unique_id}.xml"
        )
        test_db.add(source)
        test_db.flush()
        
        # Create items
        items = []
        for i in range(5):
            item = Item(
                source_id=source.id,
                title=f"Item {i} {unique_id}",
                link=f"https://example.com/article{i}_{unique_id}",
                published_at=datetime.now(timezone.utc),
                summary_short=f"Article {i} content"
            )
            test_db.add(item)
            items.append(item)
        test_db.flush()
        
        # Create person and rule
        person = Person(name=f"Test Person {unique_id}")
        test_db.add(person)
        test_db.flush()
        
        rule = WatchRule(
            label=f"Test Rule {unique_id}",
            include_rules=["Item"],
            exclude_rules=[],
            person_id=person.id
        )
        test_db.add(rule)
        test_db.commit()
        
        # Process items
        tracker = PersonTracker(test_db)
        stats = tracker.process_new_items(items)
        
        assert stats["total_items"] == 5
        assert stats["matched_items"] == 5  # All items contain "Item"
        assert stats["total_matches"] == 5
        
        # Verify timeline events
        events = test_db.query(PersonTimeline).filter(
            PersonTimeline.person_id == person.id
        ).all()
        assert len(events) == 5

