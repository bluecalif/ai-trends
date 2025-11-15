"""E2E tests for CRUD operations on all models."""
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


class TestSourceCRUD:
    """E2E tests for Source CRUD operations."""
    
    def test_create_read_source(self, test_db):
        """Test creating and reading a source."""
        unique_id = get_unique_string()
        # Create
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
        source_id = source.id
        
        # Read
        retrieved = test_db.query(Source).filter(Source.id == source_id).first()
        assert retrieved is not None
        assert retrieved.title == f"Test Source {unique_id}"
        assert retrieved.feed_url == f"https://example.com/feed_{unique_id}.xml"
        assert retrieved.is_active is True
    
    def test_update_source(self, test_db):
        """Test updating a source."""
        unique_id = get_unique_string()
        source = Source(
            title=f"Test Source {unique_id}",
            feed_url=f"https://example.com/feed_{unique_id}.xml",
            is_active=True,
        )
        test_db.add(source)
        test_db.commit()
        
        # Update
        source.is_active = False
        source.category = "Science"
        test_db.commit()
        
        # Verify
        updated = test_db.query(Source).filter(Source.id == source.id).first()
        assert updated.is_active is False
        assert updated.category == "Science"


class TestItemCRUD:
    """E2E tests for Item CRUD operations."""
    
    def test_create_read_item(self, test_db):
        """Test creating and reading an item."""
        unique_id = get_unique_string()
        # Create source first
        source = Source(
            title=f"Test Source {unique_id}",
            feed_url=f"https://example.com/feed_{unique_id}.xml",
        )
        test_db.add(source)
        test_db.flush()
        
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
        item_id = item.id
        
        # Read
        retrieved = test_db.query(Item).filter(Item.id == item_id).first()
        assert retrieved is not None
        assert retrieved.title == f"Test Item {unique_id}"
        assert retrieved.custom_tags == ["agents"]
        assert retrieved.source_id == source.id
    
    def test_item_with_entities(self, test_db):
        """Test creating item with entities."""
        unique_id = get_unique_string()
        source = Source(
            title=f"Test Source {unique_id}",
            feed_url=f"https://example.com/feed_{unique_id}.xml",
        )
        test_db.add(source)
        test_db.flush()
        
        item = Item(
            source_id=source.id,
            title=f"Test Item {unique_id}",
            link=f"https://example.com/article_{unique_id}",
            published_at=datetime.now(timezone.utc),
        )
        test_db.add(item)
        test_db.flush()
        
        # Create entities
        entity1 = Entity(name=f"GPT-4 {unique_id}", type=EntityType.TECHNOLOGY)
        entity2 = Entity(name=f"OpenAI {unique_id}", type=EntityType.ORGANIZATION)
        test_db.add(entity1)
        test_db.add(entity2)
        test_db.flush()
        
        # Add relationship
        item.entities.append(entity1)
        item.entities.append(entity2)
        test_db.commit()
        
        # Read and verify
        retrieved = test_db.query(Item).filter(Item.id == item.id).first()
        assert len(retrieved.entities) == 2
        assert any(e.name == f"GPT-4 {unique_id}" for e in retrieved.entities)
        assert any(e.name == f"OpenAI {unique_id}" for e in retrieved.entities)


class TestPersonCRUD:
    """E2E tests for Person CRUD operations."""
    
    def test_create_read_person(self, test_db):
        """Test creating and reading a person."""
        unique_id = get_unique_string()
        person = Person(
            name=f"Yann LeCun {unique_id}",
            bio="AI researcher at Meta",
        )
        test_db.add(person)
        test_db.commit()
        person_id = person.id
        
        # Read
        retrieved = test_db.query(Person).filter(Person.id == person_id).first()
        assert retrieved is not None
        assert retrieved.name == f"Yann LeCun {unique_id}"
        assert retrieved.bio == "AI researcher at Meta"
    
    def test_person_with_timeline(self, test_db):
        """Test creating person with timeline events."""
        unique_id = get_unique_string()
        person = Person(name=f"Yann LeCun {unique_id}")
        test_db.add(person)
        test_db.flush()
        
        source = Source(
            title=f"Test Source {unique_id}",
            feed_url=f"https://example.com/feed_{unique_id}.xml",
        )
        test_db.add(source)
        test_db.flush()
        
        item = Item(
            source_id=source.id,
            title=f"Test Item {unique_id}",
            link=f"https://example.com/article_{unique_id}",
            published_at=datetime.now(timezone.utc),
        )
        test_db.add(item)
        test_db.flush()
        
        # Create timeline event
        timeline = PersonTimeline(
            person_id=person.id,
            item_id=item.id,
            event_type="paper",
            description="Published new paper",
        )
        test_db.add(timeline)
        test_db.commit()
        
        # Read and verify
        retrieved = test_db.query(Person).filter(Person.id == person.id).first()
        # Access timeline through relationship if defined
        timeline_events = test_db.query(PersonTimeline).filter(
            PersonTimeline.person_id == person.id
        ).all()
        assert len(timeline_events) == 1
        assert timeline_events[0].event_type == "paper"


class TestWatchRuleCRUD:
    """E2E tests for WatchRule CRUD operations."""
    
    def test_create_read_watch_rule(self, test_db):
        """Test creating and reading a watch rule."""
        unique_id = get_unique_string()
        person = Person(name=f"Yann LeCun {unique_id}")
        test_db.add(person)
        test_db.flush()
        
        rule = WatchRule(
            label=f"LeCun Watch {unique_id}",
            include_rules=["JEPA", "Meta", "LeCun"],
            exclude_rules=["old news"],
            priority=10,
            person_id=person.id,
        )
        test_db.add(rule)
        test_db.commit()
        rule_id = rule.id
        
        # Read
        retrieved = test_db.query(WatchRule).filter(WatchRule.id == rule_id).first()
        assert retrieved is not None
        assert retrieved.label == f"LeCun Watch {unique_id}"
        assert retrieved.include_rules == ["JEPA", "Meta", "LeCun"]
        assert retrieved.priority == 10


class TestBookmarkCRUD:
    """E2E tests for Bookmark CRUD operations."""
    
    def test_create_read_bookmark(self, test_db):
        """Test creating and reading a bookmark."""
        unique_id = get_unique_string()
        source = Source(
            title=f"Test Source {unique_id}",
            feed_url=f"https://example.com/feed_{unique_id}.xml",
        )
        test_db.add(source)
        test_db.flush()
        
        item = Item(
            source_id=source.id,
            title=f"Test Item {unique_id}",
            link=f"https://example.com/article_{unique_id}",
            published_at=datetime.now(timezone.utc),
        )
        test_db.add(item)
        test_db.flush()
        
        bookmark = Bookmark(
            item_id=item.id,
            title=f"Bookmarked Item {unique_id}",
            tags=["ai", "research"],
            note="Interesting article",
        )
        test_db.add(bookmark)
        test_db.commit()
        bookmark_id = bookmark.id
        
        # Read
        retrieved = test_db.query(Bookmark).filter(Bookmark.id == bookmark_id).first()
        assert retrieved is not None
        assert retrieved.title == f"Bookmarked Item {unique_id}"
        assert retrieved.tags == ["ai", "research"]
        assert retrieved.item_id == item.id


class TestEntityCRUD:
    """E2E tests for Entity CRUD operations."""
    
    def test_create_read_entity(self, test_db):
        """Test creating and reading an entity."""
        unique_id = get_unique_string()
        entity = Entity(
            name=f"GPT-4 {unique_id}",
            type=EntityType.TECHNOLOGY,
        )
        test_db.add(entity)
        test_db.commit()
        entity_id = entity.id
        
        # Read
        retrieved = test_db.query(Entity).filter(Entity.id == entity_id).first()
        assert retrieved is not None
        assert retrieved.name == f"GPT-4 {unique_id}"
        assert retrieved.type == EntityType.TECHNOLOGY


class TestFullWorkflow:
    """E2E test for full workflow."""
    
    def test_full_item_collection_workflow(self, test_db):
        """Test complete workflow: source -> item -> entity -> person timeline."""
        unique_id = get_unique_string()
        
        # 1. Create source
        source = Source(
            title=f"Test Source {unique_id}",
            feed_url=f"https://example.com/feed_{unique_id}.xml",
        )
        test_db.add(source)
        test_db.flush()
        
        # 2. Create item
        item = Item(
            source_id=source.id,
            title=f"Test Item {unique_id}",
            link=f"https://example.com/article_{unique_id}",
            published_at=datetime.now(timezone.utc),
            custom_tags=["agents"],
        )
        test_db.add(item)
        test_db.flush()
        
        # 3. Create entities and link to item
        entity1 = Entity(name=f"GPT-4 {unique_id}", type=EntityType.TECHNOLOGY)
        entity2 = Entity(name=f"OpenAI {unique_id}", type=EntityType.ORGANIZATION)
        test_db.add(entity1)
        test_db.add(entity2)
        test_db.flush()
        
        item.entities.append(entity1)
        item.entities.append(entity2)
        
        # 4. Create person and timeline
        person = Person(name=f"Yann LeCun {unique_id}")
        test_db.add(person)
        test_db.flush()
        
        timeline = PersonTimeline(
            person_id=person.id,
            item_id=item.id,
            event_type="paper",
            description="Published new paper",
        )
        test_db.add(timeline)
        
        # 5. Create bookmark
        bookmark = Bookmark(
            item_id=item.id,
            title=f"Bookmarked {unique_id}",
            tags=["ai"],
        )
        test_db.add(bookmark)
        test_db.commit()
        
        # 6. Verify everything is linked correctly
        retrieved_item = test_db.query(Item).filter(Item.id == item.id).first()
        assert retrieved_item.source_id == source.id
        assert len(retrieved_item.entities) == 2
        
        timeline_events = test_db.query(PersonTimeline).filter(
            PersonTimeline.item_id == item.id
        ).all()
        assert len(timeline_events) == 1
        
        bookmarks = test_db.query(Bookmark).filter(Bookmark.item_id == item.id).all()
        assert len(bookmarks) == 1

