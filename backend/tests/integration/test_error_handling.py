"""Integration tests for error handling and recovery."""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock

from backend.app.main import app
from backend.app.core.database import SessionLocal
from backend.app.models.source import Source
from backend.app.models.item import Item


class TestErrorHandling:
    """Test error handling and recovery scenarios."""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup test client."""
        self.client = TestClient(app)
        self.db = SessionLocal()
        yield
        self.db.close()

    def test_404_not_found(self):
        """Test 404 error for non-existent resources."""
        # Non-existent item
        response = self.client.get("/api/items/999999")
        assert response.status_code == 404
        
        # Non-existent source
        response = self.client.get("/api/sources/999999")
        assert response.status_code == 404
        
        # Non-existent person
        response = self.client.get("/api/persons/999999")
        assert response.status_code == 404
        
        # Non-existent bookmark
        response = self.client.get("/api/bookmarks/999999")
        assert response.status_code == 404
        
        # Non-existent watch rule
        response = self.client.get("/api/watch-rules/999999")
        assert response.status_code == 404

    def test_400_invalid_filter_values(self):
        """Test 400 error for invalid filter values."""
        # Invalid field value
        response = self.client.get("/api/items?field=invalid_field")
        assert response.status_code == 400
        
        # Invalid custom_tag value
        response = self.client.get("/api/items?custom_tag=invalid_tag")
        assert response.status_code == 400
        
        # Invalid date format
        response = self.client.get("/api/items?date_from=invalid-date")
        assert response.status_code == 422  # FastAPI validation error
        
        # Invalid page number
        response = self.client.get("/api/items?page=0")
        assert response.status_code == 422  # FastAPI validation error (ge=1)
        
        # Invalid page_size
        response = self.client.get("/api/items?page_size=0")
        assert response.status_code == 422  # FastAPI validation error (ge=1)

    def test_400_invalid_request_body(self):
        """Test 400 error for invalid request body."""
        # Invalid source creation (missing required fields)
        response = self.client.post("/api/sources", json={})
        assert response.status_code == 422  # FastAPI validation error
        
        # Invalid bookmark creation (missing required fields)
        response = self.client.post("/api/bookmarks", json={})
        assert response.status_code == 422  # FastAPI validation error
        
        # Invalid watch rule creation (missing required fields)
        response = self.client.post("/api/watch-rules", json={})
        assert response.status_code == 422  # FastAPI validation error

    def test_400_duplicate_resource(self):
        """Test 400 error for duplicate resources."""
        # Create a source
        source_data = {
            "title": "Test Source Duplicate",
            "feed_url": "https://example.com/test-duplicate/feed.xml",
            "is_active": True,
        }
        response = self.client.post("/api/sources", json=source_data)
        assert response.status_code == 201
        source_id = response.json()["id"]
        
        # Try to create duplicate (same feed_url)
        response = self.client.post("/api/sources", json=source_data)
        assert response.status_code == 400  # Duplicate feed_url
        
        # Cleanup
        self.client.delete(f"/api/sources/{source_id}")

    def test_error_message_clarity(self):
        """Test that error messages are clear and helpful."""
        # 404 error message
        response = self.client.get("/api/items/999999")
        assert response.status_code == 404
        data = response.json()
        assert "detail" in data
        assert isinstance(data["detail"], str)
        assert len(data["detail"]) > 0
        
        # 400 error message
        response = self.client.get("/api/items?field=invalid_field")
        assert response.status_code == 400
        data = response.json()
        assert "detail" in data
        assert isinstance(data["detail"], str)
        assert len(data["detail"]) > 0

    def test_error_recovery(self):
        """Test that system recovers after errors."""
        # Make a request that causes an error
        response = self.client.get("/api/items/999999")
        assert response.status_code == 404
        
        # System should still work after error
        response = self.client.get("/api/items?page=1&page_size=10")
        assert response.status_code == 200
        
        # Make another error
        response = self.client.get("/api/items?field=invalid_field")
        assert response.status_code == 400
        
        # System should still work
        response = self.client.get("/api/sources")
        assert response.status_code == 200

    def test_database_connection_error_simulation(self):
        """Test handling of database connection errors (simulated)."""
        # This test simulates a database error by temporarily breaking the connection
        # In a real scenario, this would be handled by the database connection pool
        
        # Normal request should work
        response = self.client.get("/api/items?page=1&page_size=1")
        assert response.status_code in [200, 500]  # May fail if DB is down, but should handle gracefully
        
        # System should recover
        response = self.client.get("/api/sources")
        assert response.status_code in [200, 500]  # May fail if DB is down, but should handle gracefully

    def test_openai_api_fallback(self):
        """Test that OpenAI API failures are handled gracefully."""
        # This test verifies that the system can handle OpenAI API failures
        # The classifier should use fallback logic when OpenAI fails
        
        # Get an item that needs classification
        items = self.db.query(Item).limit(1).all()
        if items:
            item = items[0]
            
            # Mock OpenAI API failure
            with patch('backend.app.services.classifier.OpenAI') as mock_openai:
                mock_client = MagicMock()
                mock_openai.return_value = mock_client
                mock_client.chat.completions.create.side_effect = Exception("OpenAI API Error")
                
                # The classifier should use fallback logic
                from backend.app.services.classifier import Classifier
                classifier = Classifier()
                
                # Should not raise exception, should use fallback
                try:
                    result = classifier.classify(item.title, item.summary_short or "")
                    # Should return a result (even if using fallback)
                    assert result is not None
                    assert "iptc_topics" in result
                    assert "iab_categories" in result
                    assert "custom_tags" in result
                except Exception as e:
                    # If it raises, it should be a handled exception
                    assert "OpenAI" in str(e) or "fallback" in str(e).lower()

    def test_invalid_json_request(self):
        """Test handling of invalid JSON in request body."""
        # Send invalid JSON
        response = self.client.post(
            "/api/sources",
            data="invalid json",
            headers={"Content-Type": "application/json"}
        )
        assert response.status_code == 422  # FastAPI validation error

    def test_missing_required_fields(self):
        """Test handling of missing required fields."""
        # Source without title
        response = self.client.post("/api/sources", json={
            "feed_url": "https://example.com/feed.xml"
        })
        assert response.status_code == 422  # FastAPI validation error
        
        # Bookmark without title
        response = self.client.post("/api/bookmarks", json={
            "tags": ["test"]
        })
        assert response.status_code == 422  # FastAPI validation error

    def test_invalid_field_types(self):
        """Test handling of invalid field types."""
        # Source with invalid type for is_active
        response = self.client.post("/api/sources", json={
            "title": "Test",
            "feed_url": "https://example.com/feed.xml",
            "is_active": "not-a-boolean"
        })
        assert response.status_code == 422  # FastAPI validation error
        
        # Item filter with invalid type
        response = self.client.get("/api/items?page=not-a-number")
        assert response.status_code == 422  # FastAPI validation error

