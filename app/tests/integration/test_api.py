# app/tests/integration/test_api.py
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_read_root_endpoint():
    response = client.get("/")
    assert response.status_code == 200
    assert "Welcome" in response.json()["message"]

def test_health_check_endpoint():
    """Verifies production monitoring health checks respond successfully."""
    response = client.get("/health")
    assert response.status_code == 200
    
    data = response.json()
    # Updated: We check the status safely without looking for the removed 'error' key
    assert data["status"] == "healthy"
    assert data["database"] == "connected"