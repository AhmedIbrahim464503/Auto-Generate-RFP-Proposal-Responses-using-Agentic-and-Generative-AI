import pytest
from fastapi.testclient import TestClient

def test_health_endpoint(client: TestClient):
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "service" in data

def test_version_endpoint(client: TestClient):
    response = client.get("/api/v1/version")
    assert response.status_code == 200
    data = response.json()
    assert "version" in data
    assert data["api_v1_path"] == "/api/v1"
