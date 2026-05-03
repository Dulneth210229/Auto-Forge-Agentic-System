from pathlib import Path

from agents.tester_agent.agent import TesterAgent


def test_tester_agent_generates_and_executes_pytest_files(tmp_path: Path):
    """
    Test whether TesterAgent generates pytest files and executes them.
    """

    target = tmp_path / "sample_ecommerce_app"
    target.mkdir()

    app_file = target / "app.py"
    app_file.write_text(
        """
def list_products():
    return [{"id": 1, "name": "Demo Product"}]

def add_to_cart(product_id, quantity):
    return {"product_id": product_id, "quantity": quantity}

def checkout(cart):
    return {"order_id": 1, "status": "created"}
""",
        encoding="utf-8"
    )

    output_root = tmp_path / "outputs"

    agent = TesterAgent(output_root=str(output_root))

    result = agent.run(
        run_id="RUN-TEST",
        version="v1",
        target_path=str(target)
    )

    assert result["run_id"] == "RUN-TEST"
    assert result["stage"] == "testing"
    assert result["version"] == "v1"

    assert result["generated_tests_path"].endswith("generated_tests")
    assert result["generated_test_files_count"] == 3

    assert result["pytest_status"] in ["passed", "failed", "error"]
    assert isinstance(result["pytest_exit_code"], int)

    assert result["summary"]["total_tests"] >= 1
    assert result["summary"]["not_run"] == 0

    assert result["json_path"].endswith("TestReport_v1.json")
    assert result["markdown_path"].endswith("TestReport_v1.md")
    assert result["metadata_path"].endswith("run_metadata.json")

    assert Path(result["json_path"]).exists()
    assert Path(result["markdown_path"]).exists()
    assert Path(result["metadata_path"]).exists()

    generated_tests_path = Path(result["generated_tests_path"])

    assert (generated_tests_path / "test_project_structure.py").exists()
    assert (generated_tests_path / "test_python_syntax.py").exists()
    assert (generated_tests_path / "test_ecommerce_keywords.py").exists()