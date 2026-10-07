"""Tests for the Phase 1 health endpoint."""
from fastapi.testclient import TestClient
from app.main import app
def test_root_endpoint() -> None:
    with TestClient(app) as client: response = client.get("/")
    assert response.status_code == 200
    body = response.json(); assert body["service"] == "DocuRAG"; assert body["version"] == "0.1.0"
def test_health_endpoint() -> None:
    with TestClient(app) as client: response = client.get("/api/health")
    assert response.status_code == 200
    body = response.json(); assert "status" in body; assert body["service"] == "DocuRAG"; assert "dependencies" in body
