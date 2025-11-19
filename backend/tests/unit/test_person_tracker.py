"""Unit tests for PersonTracker service."""
import pytest
from datetime import datetime, timezone

from backend.app.services.person_tracker import PersonTracker
from backend.app.models.person import Person
from backend.app.models.watch_rule import WatchRule
from backend.app.models.item import Item
from backend.app.models.source import Source
from backend.app.models.person_timeline import PersonTimeline


def get_unique_string(prefix: str = "") -> str:
    """Generate unique string for testing."""
    import uuid
    return f"{prefix}_{uuid.uuid4().hex[:8]}"


class TestPersonTrackerMatching:
    """Test watch rule matching logic."""
    
    def test_matches_rule_include_only(self, test_db):
        """Test matching with include rules only."""
        unique_id = get_unique_string()
        
        # Create person and watch rule
        person = Person(name=f"Test Person {unique_id}")
        test_db.add(person)
        test_db.flush()
        
        rule = WatchRule(
            label=f"Test Rule {unique_id}",
            include_rules=["JEPA", "Meta"],
            exclude_rules=[],
            person_id=person.id
        )
        test_db.add(rule)
        test_db.commit()
        
        tracker = PersonTracker(test_db)
        
        # Test: should match (contains "JEPA") - text must be lowercase
        assert tracker._matches_rule("this is about jepa model", rule) is True
        
        # Test: should match (contains "Meta")
        assert tracker._matches_rule("meta ai research", rule) is True
        
        # Test: should not match (no include keywords)
        assert tracker._matches_rule("this is about gpt-4", rule) is False
    
    def test_matches_rule_exclude(self, test_db):
        """Test matching with exclude rules."""
        unique_id = get_unique_string()
        
        person = Person(name=f"Test Person {unique_id}")
        test_db.add(person)
        test_db.flush()
        
        rule = WatchRule(
            label=f"Test Rule {unique_id}",
            include_rules=["AI"],
            exclude_rules=["old news"],
            person_id=person.id
        )
        test_db.add(rule)
        test_db.commit()
        
        tracker = PersonTracker(test_db)
        
        # Test: should match (has include, no exclude) - text must be lowercase
        assert tracker._matches_rule("ai research breakthrough", rule) is True
        
        # Test: should not match (has exclude keyword)
        assert tracker._matches_rule("ai old news article", rule) is False
    
    def test_matches_rule_no_include_rules(self, test_db):
        """Test matching when include_rules is empty."""
        unique_id = get_unique_string()
        
        person = Person(name=f"Test Person {unique_id}")
        test_db.add(person)
        test_db.flush()
        
        rule = WatchRule(
            label=f"Test Rule {unique_id}",
            include_rules=[],
            exclude_rules=["spam"],
            person_id=person.id
        )
        test_db.add(rule)
        test_db.commit()
        
        tracker = PersonTracker(test_db)
        
        # Test: should match (no include rules = always match unless excluded) - text must be lowercase
        assert tracker._matches_rule("any text here", rule) is True
        
        # Test: should not match (excluded)
        assert tracker._matches_rule("this is spam", rule) is False


class TestPersonTrackerEventType:
    """Test event type inference."""
    
    def test_infer_event_type_paper(self, test_db):
        """Test inferring paper event type."""
        tracker = PersonTracker(test_db)
        
        assert tracker._infer_event_type(
            "New Research Paper Published",
            "Published in Nature journal"
        ) == "paper"
        
        assert tracker._infer_event_type(
            "arXiv preprint",
            "New research on transformers"
        ) == "paper"
    
    def test_infer_event_type_product(self, test_db):
        """Test inferring product event type."""
        tracker = PersonTracker(test_db)
        
        assert tracker._infer_event_type(
            "Product Launch",
            "Company announces new AI model"
        ) == "product"
        
        assert tracker._infer_event_type(
            "Release",
            "New version released"
        ) == "product"
    
    def test_infer_event_type_investment(self, test_db):
        """Test inferring investment event type."""
        tracker = PersonTracker(test_db)
        
        assert tracker._infer_event_type(
            "Funding Round",
            "Company raises $100M Series A"
        ) == "investment"
        
        assert tracker._infer_event_type(
            "Acquisition",
            "Company acquired by tech giant"
        ) == "investment"
    
    def test_infer_event_type_organization(self, test_db):
        """Test inferring organization event type."""
        tracker = PersonTracker(test_db)
        
        assert tracker._infer_event_type(
            "New Hire",
            "Researcher joins company"
        ) == "organization"
        
        assert tracker._infer_event_type(
            "Departure",
            "Executive leaves company"
        ) == "organization"
        
        assert tracker._infer_event_type(
            "Hired",
            "New position"
        ) == "organization"
    
    def test_infer_event_type_default(self, test_db):
        """Test default event type (research_direction)."""
        tracker = PersonTracker(test_db)
        
        assert tracker._infer_event_type(
            "General News",
            "Some general information"
        ) == "research_direction"


class TestPersonTrackerMatchItem:
    """Test matching items to persons."""
    
    def test_match_item_single_rule(self, test_db):
        """Test matching item with single watch rule."""
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
            summary_short="Meta AI research on JEPA"
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
            person_id=person.id
        )
        test_db.add(rule)
        test_db.commit()
        
        tracker = PersonTracker(test_db)
        matched = tracker.match_item(item)
        
        assert len(matched) == 1
        assert matched[0].id == person.id
        
        # Check timeline event was created
        events = test_db.query(PersonTimeline).filter(
            PersonTimeline.person_id == person.id,
            PersonTimeline.item_id == item.id
        ).all()
        assert len(events) == 1
        # Event type could be "paper" (if "research" keyword matches) or "research_direction"
        assert events[0].event_type in ["paper", "research_direction"]
    
    def test_match_item_no_match(self, test_db):
        """Test item that doesn't match any rules."""
        unique_id = get_unique_string()
        
        source = Source(
            title=f"Test Source {unique_id}",
            feed_url=f"https://example.com/feed_{unique_id}.xml"
        )
        test_db.add(source)
        test_db.flush()
        
        item = Item(
            source_id=source.id,
            title=f"Unrelated Article {unique_id}",
            link=f"https://example.com/article_{unique_id}",
            published_at=datetime.now(timezone.utc),
            summary_short="This is about something else"
        )
        test_db.add(item)
        test_db.flush()
        
        person = Person(name=f"Test Person {unique_id}")
        test_db.add(person)
        test_db.flush()
        
        rule = WatchRule(
            label=f"Test Rule {unique_id}",
            include_rules=["JEPA"],
            exclude_rules=[],
            person_id=person.id
        )
        test_db.add(rule)
        test_db.commit()
        
        tracker = PersonTracker(test_db)
        matched = tracker.match_item(item)
        
        assert len(matched) == 0
        
        # Check no timeline event was created
        events = test_db.query(PersonTimeline).filter(
            PersonTimeline.person_id == person.id
        ).all()
        assert len(events) == 0
    
    def test_match_item_duplicate_prevention(self, test_db):
        """Test that duplicate timeline events are not created."""
        unique_id = get_unique_string()
        
        source = Source(
            title=f"Test Source {unique_id}",
            feed_url=f"https://example.com/feed_{unique_id}.xml"
        )
        test_db.add(source)
        test_db.flush()
        
        item = Item(
            source_id=source.id,
            title=f"JEPA Article {unique_id}",
            link=f"https://example.com/article_{unique_id}",
            published_at=datetime.now(timezone.utc),
            summary_short="Meta JEPA research"
        )
        test_db.add(item)
        test_db.flush()
        
        person = Person(name=f"Test Person {unique_id}")
        test_db.add(person)
        test_db.flush()
        
        rule = WatchRule(
            label=f"Test Rule {unique_id}",
            include_rules=["JEPA"],
            exclude_rules=[],
            person_id=person.id
        )
        test_db.add(rule)
        test_db.commit()
        
        tracker = PersonTracker(test_db)
        
        # Match first time
        matched1 = tracker.match_item(item)
        assert len(matched1) == 1
        
        # Match second time (should not create duplicate)
        matched2 = tracker.match_item(item)
        assert len(matched2) == 1
        
        # Check only one timeline event exists
        events = test_db.query(PersonTimeline).filter(
            PersonTimeline.person_id == person.id,
            PersonTimeline.item_id == item.id
        ).all()
        assert len(events) == 1

