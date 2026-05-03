from pathlib import Path

from agents.tester_agent.agent import TesterAgent


def test_tester_agent_generates_report(tmp_path: Path):
    """
    Test whether TesterAgent generates JSON and Markdown reports.
    """

    output_root = tmp_path / "outputs"

    agent = TesterAgent(output_root=str(output_root))

    result = agent.run(
        run_id="RUN-TEST",
        version="v1",
        target_path="./sample_ecommerce_app"
    )

    assert result["run_id"] == "RUN-TEST"
    assert result["stage"] == "testing"
    assert result["version"] == "v1"

    assert result["summary"]["total_tests"] == 3
    assert result["summary"]["not_run"] == 3

    assert result["json_path"].endswith("TestReport_v1.json")
    assert result["markdown_path"].endswith("TestReport_v1.md")
    assert result["metadata_path"].endswith("run_metadata.json")

    assert Path(result["json_path"]).exists()
    assert Path(result["markdown_path"]).exists()
    assert Path(result["metadata_path"]).exists()