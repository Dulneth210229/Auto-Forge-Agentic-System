from pathlib import Path

from fastapi.testclient import TestClient

from api import app


client = TestClient(app)


def test_security_run_endpoint_without_llm(tmp_path: Path):
    """
    Test Security Agent API endpoint without real Ollama call.

    This verifies:
    - /security/run endpoint works
    - Security report paths are returned
    - Summary pack paths are returned
    - run_metadata.json path is returned
    - Security gate is included
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
    assert data["target_path"] == str(target)
    assert data["llm_enabled"] is False

    assert "json_path" in data
    assert data["json_path"].endswith("SecurityReport_v1.json")

    assert "markdown_path" in data
    assert data["markdown_path"].endswith("SecurityReport_v1.md")

    assert "summary_pack_json_path" in data
    assert data["summary_pack_json_path"].endswith("SecuritySummaryPack_v1.json")

    assert "summary_pack_markdown_path" in data
    assert data["summary_pack_markdown_path"].endswith("SecuritySummaryPack_v1.md")

    assert "metadata_path" in data
    assert data["metadata_path"].endswith("run_metadata.json")

    assert "summary" in data
    assert data["summary"]["total_findings"] >= 1

    assert "dependency_vulnerabilities_count" in data
    assert "llm_findings_count" in data
    assert data["llm_findings_count"] == 0

    assert "deduplication" in data
    assert "findings_before_deduplication" in data["deduplication"]
    assert "findings_after_deduplication" in data["deduplication"]
    assert "duplicates_removed" in data["deduplication"]

    assert "security_gate" in data
    assert data["security_gate"]["status"] in ["PASS", "WARN", "FAIL"]
    assert "reason" in data["security_gate"]
    assert "policy" in data["security_gate"]
    assert "blocking_findings" in data["security_gate"]

    assert data["traceability_mapped"] is True

    assert "fix_suggestions_count" in data
    assert data["fix_suggestions_count"] >= 1

    # Optional: verify that expected output artifacts were physically created.
    assert Path(data["json_path"]).exists()
    assert Path(data["markdown_path"]).exists()
    assert Path(data["summary_pack_json_path"]).exists()
    assert Path(data["summary_pack_markdown_path"]).exists()
    assert Path(data["metadata_path"]).exists()


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

    data = response.json()

    assert "detail" in data
    assert "Target path does not exist" in data["detail"]