"""Unit tests for database models."""
import pytest
import uuid
from datetime import datetime, timezone
from backend.app.models import (
    Source,
    Item,
    Person,
    PersonTimeline,
    WatchRule,
    Bookmark,
    Entity,
    EntityType,
)


def get_unique_string(prefix: str = "") -> str:
    """Generate unique string for test data."""
    return f"{prefix}_{uuid.uuid4().hex[:8]}"


class TestSourceModel:
    """Test Source model."""
    
    def test_create_source(self, test_db):
        """Test Source model creation."""
        unique_id = get_unique_string()
        source = Source(
            title=f"Test Source {unique_id}",
            feed_url=f"https://example.com/feed_{unique_id}.xml",
            site_url="https://example.com",
            category="Technology",
            lang="en",
            is_active=True,
        )
        test_db.add(source)
        test_db.commit()
        
        assert source.id is not None
        assert source.title == f"Test Source {unique_id}"
        assert f"feed_{unique_id}" in source.feed_url
        assert source.is_active is True
        assert source.created_at is not None
        assert source.updated_at is not None
    
    def test_source_unique_feed_url(self, test_db):
        """Test Source feed_url uniqueness constraint."""
        unique_url = f"https://example.com/feed_{get_unique_string()}.xml"
        source1 = Source(
            title="Source 1",
            feed_url=unique_url,
        )
        test_db.add(source1)
        test_db.commit()
        
        source2 = Source(
            title="Source 2",
            feed_url=unique_url,  # Duplicate
        )
        test_db.add(source2)
        
        with pytest.raises(Exception):  # IntegrityError
            test_db.commit()


class TestItemModel:
    """Test Item model."""
    
    def test_create_item(self, test_db):
        """Test Item model creation."""
        unique_id = get_unique_string()
        # Create source first
        source = Source(
            title=f"Test Source {unique_id}",
            feed_url=f"https://example.com/feed_{unique_id}.xml",
        )
        test_db.add(source)
        test_db.commit()
        
        # Create item
        item = Item(
            source_id=source.id,
            title=f"Test Item {unique_id}",
            summary_short="Test summary",
            link=f"https://example.com/article_{unique_id}",
            published_at=datetime.now(timezone.utc),
            author="Test Author",
            iptc_topics=["technology"],
            iab_categories=["Technology"],
            custom_tags=["agents"],
        )
        test_db.add(item)
        test_db.commit()
        
        assert item.id is not None
        assert item.title == f"Test Item {unique_id}"
        assert item.source_id == source.id
        assert item.custom_tags == ["agents"]
        assert f"article_{unique_id}" in item.link
    
    def test_item_foreign_key_relationship(self, test_db):
        """Test Item-Source relationship."""
        unique_id = get_unique_string()
        source = Source(
            title=f"Test Source {unique_id}",
            feed_url=f"https://example.com/feed_{unique_id}.xml",
        )
        test_db.add(source)
        test_db.commit()
        
        item = Item(
            source_id=source.id,
            title=f"Test Item {unique_id}",
            link=f"https://example.com/article_{unique_id}",
            published_at=datetime.now(timezone.utc),
        )
        test_db.add(item)
        test_db.commit()
        
        # Test relationship
        assert item.source.id == source.id
        assert item in source.items
    
    def test_item_unique_link(self, test_db):
        """Test Item link uniqueness constraint."""
        unique_id = get_unique_string()
        source = Source(
            title=f"Test Source {unique_id}",
            feed_url=f"https://example.com/feed_{unique_id}.xml",
        )
        test_db.add(source)
        test_db.commit()
        
        unique_link = f"https://example.com/article_{unique_id}"
        item1 = Item(
            source_id=source.id,
            title="Item 1",
            link=unique_link,
            published_at=datetime.now(timezone.utc),
        )
        test_db.add(item1)
        test_db.commit()
        
        item2 = Item(
            source_id=source.id,
            title="Item 2",
            link=unique_link,  # Duplicate
            published_at=datetime.now(timezone.utc),
        )
        test_db.add(item2)
        
        with pytest.raises(Exception):  # IntegrityError
            test_db.commit()


class TestPersonModel:
    """Test Person model."""
    
    def test_create_person(self, test_db):
        """Test Person model creation."""
        unique_id = get_unique_string()
        person = Person(
            name=f"Yann LeCun {unique_id}",
            bio="AI researcher at Meta",
        )
        test_db.add(person)
        test_db.commit()
        
        assert person.id is not None
        assert person.name == f"Yann LeCun {unique_id}"
        assert person.bio == "AI researcher at Meta"
        assert person.created_at is not None
    
    def test_person_unique_name(self, test_db):
        """Test Person name uniqueness constraint."""
        unique_name = f"Yann LeCun {get_unique_string()}"
        person1 = Person(name=unique_name)
        test_db.add(person1)
        test_db.commit()
        
        person2 = Person(name=unique_name)  # Duplicate
        test_db.add(person2)
        
        with pytest.raises(Exception):  # IntegrityError
            test_db.commit()


class TestPersonTimelineModel:
    """Test PersonTimeline model."""
    
    def test_create_person_timeline(self, test_db):
        """Test PersonTimeline model creation."""
        unique_id = get_unique_string()
        # Create person and item
        person = Person(name=f"Yann LeCun {unique_id}")
        test_db.add(person)
        test_db.flush()  # Flush to get person.id
        
        source = Source(
            title=f"Test Source {unique_id}",
            feed_url=f"https://example.com/feed_{unique_id}.xml",
        )
        test_db.add(source)
        test_db.flush()  # Flush to get source.id
        
        item = Item(
            source_id=source.id,
            title=f"Test Item {unique_id}",
            link=f"https://example.com/article_{unique_id}",
            published_at=datetime.now(timezone.utc),
        )
        test_db.add(item)
        test_db.flush()  # Flush to get item.id
        
        # Create timeline event
        timeline = PersonTimeline(
            person_id=person.id,
            item_id=item.id,
            event_type="paper",
            description="Published new paper",
        )
        test_db.add(timeline)
        test_db.commit()
        
        assert timeline.id is not None
        assert timeline.person_id == person.id
        assert timeline.item_id == item.id
        assert timeline.event_type == "paper"
        assert timeline.person.id == person.id


class TestWatchRuleModel:
    """Test WatchRule model."""
    
    def test_create_watch_rule(self, test_db):
        """Test WatchRule model creation."""
        unique_id = get_unique_string()
        person = Person(name=f"Yann LeCun {unique_id}")
        test_db.add(person)
        test_db.commit()
        
        rule = WatchRule(
            label=f"LeCun Watch {unique_id}",
            include_rules=["JEPA", "Meta", "LeCun"],
            exclude_rules=["old news"],
            priority=10,
            person_id=person.id,
        )
        test_db.add(rule)
        test_db.commit()
        
        assert rule.id is not None
        assert rule.label == f"LeCun Watch {unique_id}"
        assert rule.include_rules == ["JEPA", "Meta", "LeCun"]
        assert rule.exclude_rules == ["old news"]
        assert rule.priority == 10
        assert rule.person_id == person.id
        assert rule.person.id == person.id


class TestEntityModel:
    """Test Entity model."""
    
    def test_create_entity(self, test_db):
        """Test Entity model creation."""
        unique_id = get_unique_string()
        entity = Entity(
            name=f"GPT-4 {unique_id}",
            type=EntityType.TECHNOLOGY,
        )
        test_db.add(entity)
        test_db.commit()
        
        assert entity.id is not None
        assert entity.name == f"GPT-4 {unique_id}"
        assert entity.type == EntityType.TECHNOLOGY
    
    def test_entity_unique_name(self, test_db):
        """Test Entity name uniqueness constraint."""
        unique_name = f"GPT-4 {get_unique_string()}"
        entity1 = Entity(name=unique_name, type=EntityType.TECHNOLOGY)
        test_db.add(entity1)
        test_db.commit()
        
        entity2 = Entity(name=unique_name, type=EntityType.TECHNOLOGY)  # Duplicate
        test_db.add(entity2)
        
        with pytest.raises(Exception):  # IntegrityError
            test_db.commit()


class TestItemEntityRelationship:
    """Test Item-Entity many-to-many relationship."""
    
    def test_item_entity_relationship(self, test_db):
        """Test Item-Entity many-to-many relationship."""
        unique_id = get_unique_string()
        # Create source and item
        source = Source(
            title=f"Test Source {unique_id}",
            feed_url=f"https://example.com/feed_{unique_id}.xml",
        )
        test_db.add(source)
        test_db.flush()  # Flush to get source.id
        
        item = Item(
            source_id=source.id,
            title=f"Test Item {unique_id}",
            link=f"https://example.com/article_{unique_id}",
            published_at=datetime.now(timezone.utc),
        )
        test_db.add(item)
        test_db.flush()  # Flush to get item.id
        
        # Create entities
        entity1 = Entity(name=f"GPT-4 {unique_id}", type=EntityType.TECHNOLOGY)
        entity2 = Entity(name=f"OpenAI {unique_id}", type=EntityType.ORGANIZATION)
        test_db.add(entity1)
        test_db.add(entity2)
        test_db.flush()  # Flush to get entity IDs
        
        # Add relationship
        item.entities.append(entity1)
        item.entities.append(entity2)
        test_db.commit()
        
        # Refresh to load relationships
        test_db.refresh(item)
        test_db.refresh(entity1)
        test_db.refresh(entity2)
        
        # Test relationship
        assert len(item.entities) == 2
        assert entity1 in item.entities
        assert entity2 in item.entities
        assert item in entity1.items
        assert item in entity2.items


class TestBookmarkModel:
    """Test Bookmark model."""
    
    def test_create_bookmark(self, test_db):
        """Test Bookmark model creation."""
        unique_id = get_unique_string()
        # Create source and item
        source = Source(
            title=f"Test Source {unique_id}",
            feed_url=f"https://example.com/feed_{unique_id}.xml",
        )
        test_db.add(source)
        test_db.flush()  # Flush to get source.id
        
        item = Item(
            source_id=source.id,
            title=f"Test Item {unique_id}",
            link=f"https://example.com/article_{unique_id}",
            published_at=datetime.now(timezone.utc),
        )
        test_db.add(item)
        test_db.flush()  # Flush to get item.id
        
        # Create bookmark
        bookmark = Bookmark(
            item_id=item.id,
            title=f"Bookmarked Item {unique_id}",
            tags=["ai", "research"],
            note="Interesting article",
        )
        test_db.add(bookmark)
        test_db.commit()
        
        assert bookmark.id is not None
        assert bookmark.item_id == item.id
        assert bookmark.title == f"Bookmarked Item {unique_id}"
        assert bookmark.tags == ["ai", "research"]
        assert bookmark.note == "Interesting article"

