from pathlib import Path
from unittest.mock import patch

from agents.security_agent.agent import SecurityAgent
from tools.llm.provider import LLMProvider


class FakeLLMProvider(LLMProvider):
    """
    Fake LLM provider used to test SecurityAgent with enable_llm=True.
    """

    def generate(self, prompt: str) -> str:
        return """
{
  "findings": [
    {
      "title": "LLM test finding",
      "description": "This is a test LLM finding.",
      "severity": "Medium",
      "line": 1,
      "cwe": "CWE-20",
      "recommendation": "Fix the test issue.",
      "confidence": 0.8
    }
  ]
}
"""


def test_security_agent_runs_without_llm(tmp_path: Path):
    """
    Checks whether SecurityAgent can run with LLM disabled.
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

    output_root = tmp_path / "outputs"

    agent = SecurityAgent(output_root=str(output_root))

    result = agent.run(
        run_id="RUN-TEST",
        version="v1",
        target_path=str(target),
        enable_llm=False
    )

    assert result["run_id"] == "RUN-TEST"
    assert result["llm_enabled"] is False
    assert result["llm_findings_count"] == 0
    assert result["summary"]["total_findings"] >= 2

    assert Path(result["json_path"]).exists()
    assert Path(result["markdown_path"]).exists()


def test_security_agent_runs_with_fake_llm(tmp_path: Path):
    """
    Checks whether SecurityAgent can run with LLM enabled using a fake provider.
    This avoids calling real Ollama during tests.
    """

    target = tmp_path / "sample_app"
    target.mkdir()

    app_file = target / "app.py"
    app_file.write_text(
        """
def process_input(user_input):
    return user_input
""",
        encoding="utf-8"
    )

    output_root = tmp_path / "outputs"

    with patch(
        "agents.security_agent.agent.OllamaProvider",
        return_value=FakeLLMProvider()
    ):
        agent = SecurityAgent(output_root=str(output_root))

        result = agent.run(
            run_id="RUN-TEST",
            version="v1",
            target_path=str(target),
            enable_llm=True
        )

    assert result["run_id"] == "RUN-TEST"
    assert result["llm_enabled"] is True
    assert result["llm_findings_count"] >= 1
    assert result["summary"]["total_findings"] >= 1

    assert Path(result["json_path"]).exists()
    assert Path(result["markdown_path"]).exists()