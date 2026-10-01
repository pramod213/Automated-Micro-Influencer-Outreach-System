"""Tests for the health endpoint."""

import pytest
from fastapi.testclient import TestClient
from app.main import app


@pytest.fixture
def client() -> TestClient:
    """Create a test client for the FastAPI app."""
    return TestClient(app)


def test_health_endpoint_exists(client: TestClient):
    """Test that /health endpoint exists and returns 200."""
    response = client.get("/health")
    assert response.status_code == 200


def test_health_endpoint_returns_correct_structure(client: TestClient):
    """Test that /health returns expected JSON structure."""
    response = client.get("/health")
    data = response.json()
    assert "status" in data
    assert data["status"] == "healthy"


def test_app_metadata(client: TestClient):
    """Test that app has correct metadata."""
    response = client.get("/openapi.json")
    assert response.status_code == 200
    openapi = response.json()
    assert openapi["info"]["title"] == "Automated Micro-Influencer Outreach System"
    assert openapi["info"]["version"] == "0.1.0"