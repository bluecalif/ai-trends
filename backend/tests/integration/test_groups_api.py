"""Integration test for groups API (basic smoke)."""
import pytest
from fastapi.testclient import TestClient

from backend.app.main import app


@pytest.mark.integration
def test_groups_list_endpoint_smoke():
    client = TestClient(app)
    # use today's date string in ISO (YYYY-MM-DD)
    from datetime import datetime, timezone

    since = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    resp = client.get(f"/api/groups?since={since}&kind=new&page=1&page_size=5")
    assert resp.status_code == 200
    data = resp.json()
    assert "groups" in data
    assert "total" in data


