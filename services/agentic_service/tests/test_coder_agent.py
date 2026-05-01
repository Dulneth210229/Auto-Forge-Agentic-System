import pytest
import tempfile
import json
import shutil
from pathlib import Path
from services.agentic_service.agents.coder_agent.agent import CoderAgent

@pytest.fixture
def temp_env():
    # Create a temporary directory for output
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    # Cleanup
    shutil.rmtree(temp_dir)

def test_coder_agent_generate(temp_env):
    run_id = "RUN-TEST-001"
    srs_version = "v1"
    code_version = "v1"
    
    # 1. Create a temporary SRS_v1.json
    srs_dir = Path(temp_env) / "runs" / run_id / "srs" / srs_version
    srs_dir.mkdir(parents=True, exist_ok=True)
    srs_file = srs_dir / f"SRS_{srs_version}.json"
    
    mock_srs = {
        "metadata": {"project_name": "Test Commerce"},
        "sections": {
            "functional_requirements": [
                {"id": "REQ-01", "title": "Product Catalog"}
            ]
        }
    }
    with open(srs_file, "w", encoding="utf-8") as f:
        json.dump(mock_srs, f)
        
    # 2. Run coder_agent.generate_code()
    agent = CoderAgent(output_dir=temp_env)
    result = agent.generate_code(run_id=run_id, srs_version=srs_version, code_version=code_version)
    
    assert result["status"] == "success"
    
    # 3. Assert outputs exist
    base_dir = Path(temp_env) / "runs" / run_id / "code" / code_version / "generated_app"
    
    assert (base_dir / "backend" / "main.py").exists()
    assert (base_dir / "frontend" / "index.html").exists()
    assert (base_dir / "docker-compose.yml").exists()
    
    manifest_path = Path(temp_env) / "runs" / run_id / "code" / code_version / f"CodeManifest_{code_version}.json"
    assert manifest_path.exists()
