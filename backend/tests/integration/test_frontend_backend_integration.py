"""Integration tests for frontend-backend API contract validation.

This test verifies that backend API responses match the frontend TypeScript type definitions.
"""

import pytest
from fastapi.testclient import TestClient
from datetime import datetime, timezone

from backend.app.main import app
from backend.app.core.database import SessionLocal
from backend.app.core.constants import PRD_RSS_SOURCES
from backend.app.services.rss_collector import RSSCollector
from backend.app.models.source import Source
from backend.app.models.item import Item
from backend.app.models.person import Person
from backend.app.models.bookmark import Bookmark
from backend.app.models.watch_rule import WatchRule


def get_unique_string(prefix: str = "") -> str:
    """Generate unique string for testing."""
    import uuid
    return f"{prefix}_{uuid.uuid4().hex[:8]}"


class TestFrontendBackendIntegration:
    """Test frontend-backend API contract compatibility."""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup test client and database."""
        self.client = TestClient(app)
        self.db = SessionLocal()
        
        # Ensure sources exist
        for source_data in PRD_RSS_SOURCES:
            source = self.db.query(Source).filter(
                Source.feed_url == source_data["feed_url"]
            ).first()
            if not source:
                source = Source(
                    title=source_data["title"],
                    feed_url=source_data["feed_url"],
                    site_url=source_data.get("site_url"),
                    is_active=True,
                )
                self.db.add(source)
        self.db.commit()
        
        # Get or create test data
        self.items = self.db.query(Item).order_by(Item.published_at.desc()).limit(10).all()
        if len(self.items) == 0:
            collector = RSSCollector(self.db)
            active_sources = self.db.query(Source).filter(Source.is_active == True).all()
            for source in active_sources[:2]:  # Limit to 2 sources for speed
                try:
                    collector.collect_source(source)
                except Exception:
                    pass
            self.items = self.db.query(Item).order_by(Item.published_at.desc()).limit(10).all()
        
        yield
        
        self.db.close()

    def test_items_api_contract(self):
        """Test Items API response matches frontend ItemResponse type."""
        # GET /api/items
        response = self.client.get("/api/items?page=1&page_size=5")
        assert response.status_code == 200
        data = response.json()
        
        # Verify ItemListResponse structure
        assert "items" in data
        assert "total" in data
        assert "page" in data
        assert "page_size" in data
        assert isinstance(data["items"], list)
        assert isinstance(data["total"], int)
        assert isinstance(data["page"], int)
        assert isinstance(data["page_size"], int)
        
        # Verify ItemResponse structure for first item
        if len(data["items"]) > 0:
            item = data["items"][0]
            required_fields = [
                "id", "source_id", "title", "link", "published_at",
                "iptc_topics", "iab_categories", "custom_tags",
                "created_at", "updated_at"
            ]
            for field in required_fields:
                assert field in item, f"Missing field: {field}"
            
            # Verify types
            assert isinstance(item["id"], int)
            assert isinstance(item["source_id"], int)
            assert isinstance(item["title"], str)
            assert isinstance(item["link"], str)
            assert isinstance(item["published_at"], str)  # ISO date string
            assert isinstance(item["iptc_topics"], list)
            assert isinstance(item["iab_categories"], list)
            assert isinstance(item["custom_tags"], list)
            assert isinstance(item["created_at"], str)  # ISO date string
            assert isinstance(item["updated_at"], str)  # ISO date string
            
            # Optional fields
            if "summary_short" in item:
                assert item["summary_short"] is None or isinstance(item["summary_short"], str)
            if "author" in item:
                assert item["author"] is None or isinstance(item["author"], str)
            if "thumbnail_url" in item:
                assert item["thumbnail_url"] is None or isinstance(item["thumbnail_url"], str)
            if "field" in item:
                assert item["field"] is None or isinstance(item["field"], str)
            if "dup_group_id" in item:
                assert item["dup_group_id"] is None or isinstance(item["dup_group_id"], int)

    def test_items_api_filters(self):
        """Test Items API filters match frontend expectations."""
        # Test custom_tag filter
        response = self.client.get("/api/items?custom_tag=agents&page=1&page_size=5")
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        
        # Test field filter
        response = self.client.get("/api/items?field=research&page=1&page_size=5")
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        
        # Test date filters
        response = self.client.get("/api/items?date_from=2024-01-01&date_to=2024-12-31")
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        
        # Test pagination
        response = self.client.get("/api/items?page=2&page_size=10")
        assert response.status_code == 200
        data = response.json()
        assert data["page"] == 2
        assert data["page_size"] == 10
        
        # Test sorting
        response = self.client.get("/api/items?order_by=published_at&order_desc=true")
        assert response.status_code == 200
        data = response.json()
        assert "items" in data

    def test_item_detail_api_contract(self):
        """Test Item detail API response matches frontend ItemResponse type."""
        if not self.items:
            pytest.skip("No items in database")
        
        item_id = self.items[0].id
        response = self.client.get(f"/api/items/{item_id}")
        assert response.status_code == 200
        data = response.json()
        
        # Verify ItemResponse structure
        required_fields = [
            "id", "source_id", "title", "link", "published_at",
            "iptc_topics", "iab_categories", "custom_tags",
            "created_at", "updated_at"
        ]
        for field in required_fields:
            assert field in data, f"Missing field: {field}"
        
        assert data["id"] == item_id

    def test_sources_api_contract(self):
        """Test Sources API response matches frontend SourceResponse type."""
        # GET /api/sources
        response = self.client.get("/api/sources")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        
        if len(data) > 0:
            source = data[0]
            required_fields = [
                "id", "title", "feed_url", "lang", "is_active",
                "created_at", "updated_at"
            ]
            for field in required_fields:
                assert field in source, f"Missing field: {field}"
            
            # Verify types
            assert isinstance(source["id"], int)
            assert isinstance(source["title"], str)
            assert isinstance(source["feed_url"], str)
            assert isinstance(source["lang"], str)
            assert isinstance(source["is_active"], bool)
            assert isinstance(source["created_at"], str)  # ISO date string
            assert isinstance(source["updated_at"], str)  # ISO date string
            
            # Optional fields
            if "site_url" in source:
                assert source["site_url"] is None or isinstance(source["site_url"], str)
            if "category" in source:
                assert source["category"] is None or isinstance(source["category"], str)

    def test_sources_crud_contract(self):
        """Test Sources CRUD operations match frontend expectations."""
        # Create
        unique_id = get_unique_string("test")
        create_data = {
            "title": f"Test Source {unique_id}",
            "feed_url": f"https://example.com/{unique_id}/feed.xml",
            "site_url": f"https://example.com/{unique_id}",
            "is_active": True,
        }
        response = self.client.post("/api/sources", json=create_data)
        assert response.status_code == 201
        created = response.json()
        assert created["title"] == create_data["title"]
        source_id = created["id"]
        
        # Read
        response = self.client.get(f"/api/sources/{source_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == source_id
        
        # Update
        update_data = {"title": f"Updated {unique_id}"}
        response = self.client.put(f"/api/sources/{source_id}", json=update_data)
        assert response.status_code == 200
        updated = response.json()
        assert updated["title"] == update_data["title"]
        
        # Delete
        response = self.client.delete(f"/api/sources/{source_id}")
        assert response.status_code == 204

    def test_persons_api_contract(self):
        """Test Persons API response matches frontend PersonResponse type."""
        # GET /api/persons
        response = self.client.get("/api/persons")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        
        if len(data) > 0:
            person = data[0]
            required_fields = [
                "id", "name", "created_at", "updated_at"
            ]
            for field in required_fields:
                assert field in person, f"Missing field: {field}"
            
            # Verify types
            assert isinstance(person["id"], int)
            assert isinstance(person["name"], str)
            assert isinstance(person["created_at"], str)  # ISO date string
            assert isinstance(person["updated_at"], str)  # ISO date string
            
            # Optional fields
            if "bio" in person:
                assert person["bio"] is None or isinstance(person["bio"], str)

    def test_person_detail_api_contract(self):
        """Test Person detail API response matches frontend PersonDetailResponse type."""
        persons = self.db.query(Person).limit(1).all()
        if not persons:
            pytest.skip("No persons in database")
        
        person_id = persons[0].id
        response = self.client.get(
            f"/api/persons/{person_id}?include_timeline=true&include_graph=true"
        )
        assert response.status_code == 200
        data = response.json()
        
        # Verify PersonDetailResponse structure
        required_fields = ["id", "name", "created_at", "updated_at", "timeline"]
        for field in required_fields:
            assert field in data, f"Missing field: {field}"
        
        assert isinstance(data["timeline"], list)
        assert "relationship_graph" in data

    def test_bookmarks_api_contract(self):
        """Test Bookmarks API response matches frontend BookmarkResponse type."""
        # GET /api/bookmarks
        response = self.client.get("/api/bookmarks")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        
        # Create bookmark
        if self.items:
            item = self.items[0]
            unique_id = get_unique_string("bookmark")
            create_data = {
                "item_id": item.id,
                "title": f"Test Bookmark {unique_id}",
                "tags": ["test", "integration"],
                "note": "Test bookmark for integration test",
            }
            response = self.client.post("/api/bookmarks", json=create_data)
            assert response.status_code == 201
            created = response.json()
            
            # Verify BookmarkResponse structure
            required_fields = ["id", "item_id", "title", "tags", "created_at"]
            for field in required_fields:
                assert field in created, f"Missing field: {field}"
            
            assert isinstance(created["id"], int)
            assert isinstance(created["item_id"], int)
            assert isinstance(created["title"], str)
            assert isinstance(created["tags"], list)
            assert isinstance(created["created_at"], str)  # ISO date string
            
            # Delete
            bookmark_id = created["id"]
            response = self.client.delete(f"/api/bookmarks/{bookmark_id}")
            assert response.status_code == 204

    def test_watch_rules_api_contract(self):
        """Test Watch Rules API response matches frontend WatchRuleResponse type."""
        # GET /api/watch-rules
        response = self.client.get("/api/watch-rules")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        
        if len(data) > 0:
            rule = data[0]
            required_fields = [
                "id", "label", "include_rules", "exclude_rules",
                "required_keywords", "optional_keywords", "priority",
                "created_at", "updated_at"
            ]
            for field in required_fields:
                assert field in rule, f"Missing field: {field}"
            
            # Verify types
            assert isinstance(rule["id"], int)
            assert isinstance(rule["label"], str)
            assert isinstance(rule["include_rules"], list)
            assert isinstance(rule["exclude_rules"], list)
            assert isinstance(rule["required_keywords"], list)
            assert isinstance(rule["optional_keywords"], list)
            assert isinstance(rule["priority"], int)
            assert isinstance(rule["created_at"], str)  # ISO date string
            assert isinstance(rule["updated_at"], str)  # ISO date string
            
            # Optional fields
            if "person_id" in rule:
                assert rule["person_id"] is None or isinstance(rule["person_id"], int)

    def test_constants_api_contract(self):
        """Test Constants API response matches frontend ConstantsResponse type."""
        # GET /api/constants/fields
        response = self.client.get("/api/constants/fields")
        assert response.status_code == 200
        data = response.json()
        assert "fields" in data
        assert isinstance(data["fields"], list)
        
        # GET /api/constants/custom-tags
        response = self.client.get("/api/constants/custom-tags")
        assert response.status_code == 200
        data = response.json()
        assert "tags" in data
        assert isinstance(data["tags"], list)

    def test_groups_api_contract(self):
        """Test Groups API response matches frontend GroupsListResponse type."""
        from datetime import date, timedelta
        
        # GET /api/groups
        since_date = (date.today() - timedelta(days=21)).isoformat()
        response = self.client.get(f"/api/groups?since={since_date}&page=1&page_size=10")
        assert response.status_code == 200
        data = response.json()
        
        # Verify GroupsListResponse structure
        assert "total" in data
        assert "page" in data
        assert "page_size" in data
        assert "groups" in data
        assert isinstance(data["groups"], list)
        
        if len(data["groups"]) > 0:
            group = data["groups"][0]
            required_fields = [
                "dup_group_id", "first_seen_at", "last_updated_at",
                "member_count", "representative"
            ]
            for field in required_fields:
                assert field in group, f"Missing field: {field}"
            
            assert isinstance(group["dup_group_id"], int)
            assert isinstance(group["member_count"], int)
            assert isinstance(group["representative"], dict)

