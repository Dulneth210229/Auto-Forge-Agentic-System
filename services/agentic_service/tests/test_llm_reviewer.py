from pathlib import Path

from agents.security_agent.llm_reviewer import LLMSecureCodeReviewer
from agents.security_agent.scanners.base import FindingFactory
from tools.llm.provider import LLMProvider


class FakeGoodLLMProvider(LLMProvider):
    """
    Fake LLM provider for testing successful JSON output.
    No real Ollama call is made.
    """

    def generate(self, prompt: str) -> str:
        return """
{
  "findings": [
    {
      "title": "Missing input validation",
      "description": "User input is processed without validation.",
      "severity": "High",
      "line": 5,
      "cwe": "CWE-20",
      "recommendation": "Validate and sanitize user input.",
      "confidence": 0.9
    }
  ]
}
"""


class FakeBadLLMProvider(LLMProvider):
    """
    Fake LLM provider for testing invalid JSON handling.
    """

    def generate(self, prompt: str) -> str:
        return "This is not valid JSON"


def test_llm_reviewer_parses_valid_json(tmp_path: Path):
    """
    Checks whether LLMSecureCodeReviewer can parse valid LLM JSON output
    and convert it into SecurityFinding objects.
    """

    test_file = tmp_path / "app.py"
    test_file.write_text(
        """
def search(keyword):
    return keyword
""",
        encoding="utf-8"
    )

    reviewer = LLMSecureCodeReviewer(
        llm_provider=FakeGoodLLMProvider(),
        factory=FindingFactory()
    )

    findings = reviewer.review_file(test_file)

    assert len(findings) == 1
    assert findings[0].title == "Missing input validation"
    assert findings[0].severity == "High"
    assert findings[0].detection_method == "LLM"

    assert len(reviewer.llm_findings) == 1
    assert reviewer.llm_findings[0]["source"] == "ollama"


def test_llm_reviewer_handles_invalid_json(tmp_path: Path):
    """
    Checks whether the LLM reviewer fails safely when the LLM returns invalid JSON.
    """

    test_file = tmp_path / "app.py"
    test_file.write_text(
        """
def example():
    return "hello"
""",
        encoding="utf-8"
    )

    reviewer = LLMSecureCodeReviewer(
        llm_provider=FakeBadLLMProvider(),
        factory=FindingFactory()
    )

    findings = reviewer.review_file(test_file)

    assert len(findings) == 1
    assert findings[0].title == "LLM review failed"
    assert findings[0].severity == "Low"
    assert findings[0].detection_method == "LLM"

    assert len(reviewer.llm_findings) == 1
    assert reviewer.llm_findings[0]["title"] == "LLM review failed"


def test_llm_reviewer_selects_supported_files_only(tmp_path: Path):
    """
    Checks whether only supported source files are selected for review.
    """

    py_file = tmp_path / "app.py"
    js_file = tmp_path / "frontend.js"
    txt_file = tmp_path / "notes.txt"

    py_file.write_text("print('hello')", encoding="utf-8")
    js_file.write_text("console.log('hello')", encoding="utf-8")
    txt_file.write_text("plain text", encoding="utf-8")

    reviewer = LLMSecureCodeReviewer(
        llm_provider=FakeGoodLLMProvider(),
        factory=FindingFactory()
    )

    selected_files = reviewer._select_files_for_review(tmp_path)
    selected_names = [file.name for file in selected_files]

    assert "app.py" in selected_names
    assert "frontend.js" in selected_names
    assert "notes.txt" not in selected_names