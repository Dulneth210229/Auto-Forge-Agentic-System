from fastapi.testclient import TestClient
from api import app

client = TestClient(app)


def test_health_endpoint():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_validate_intake_endpoint():
    payload = {
        "project_name": "AutoForge Shop",
        "business_goal": "Build an E-commerce platform for online product sales.",
        "target_users": ["Customer", "Admin"]
    }

    response = client.post("/requirements/intake/validate", json=payload)

    assert response.status_code == 200
    assert response.json()["valid"] is True