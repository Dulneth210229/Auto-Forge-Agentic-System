from pathlib import Path

from fastapi.testclient import TestClient

from api import app


client = TestClient(app)


def test_security_run_endpoint_without_llm(tmp_path: Path):
    """
    Test Security Agent API endpoint without real Ollama call.
    """

    target = tmp_path / "sample_app"
    target.mkdir()

    app_file = target / "app.py"
    app_file.write_text(
        """
API_KEY = "test-secret-key"

def dangerous(user_input):
    return eval(user_input)
""",
        encoding="utf-8"
    )

    response = client.post(
        "/security/run",
        json={
            "run_id": "RUN-API-TEST",
            "version": "v1",
            "target_path": str(target),
            "enable_llm": False
        }
    )

    assert response.status_code == 200

    data = response.json()

    assert data["run_id"] == "RUN-API-TEST"
    assert data["stage"] == "security"
    assert data["version"] == "v1"
    assert data["llm_enabled"] is False
    assert data["summary"]["total_findings"] >= 1
    assert "security_gate" in data
    assert "json_path" in data
    assert "summary_pack_json_path" in data


def test_security_run_endpoint_invalid_target():
    """
    Test Security Agent API endpoint with invalid target path.
    """

    response = client.post(
        "/security/run",
        json={
            "run_id": "RUN-API-TEST",
            "version": "v1",
            "target_path": "./folder_that_does_not_exist",
            "enable_llm": False
        }
    )

    assert response.status_code == 404