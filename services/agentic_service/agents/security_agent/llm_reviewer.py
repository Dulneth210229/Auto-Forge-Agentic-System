import json
import re
from pathlib import Path
from typing import List, Dict, Any

from agents.security_agent.schemas import SecurityFinding
from agents.security_agent.scanners.base import FindingFactory
from tools.llm.provider import LLMProvider


class LLMSecureCodeReviewer:
    """
    LLM-assisted secure code reviewer.

    This class:
    - Selects risky files from the target project
    - Sends code snippets to Ollama
    - Forces strict JSON output
    - Converts LLM findings into SecurityFinding records
    """

    SUPPORTED_EXTENSIONS = {
        ".py", ".js", ".jsx", ".ts", ".tsx"
    }

    MAX_FILES_TO_REVIEW = 3
    MAX_CHARS_PER_FILE = 6000

    def __init__(self, llm_provider: LLMProvider, factory: FindingFactory):
        self.llm_provider = llm_provider
        self.factory = factory
        self.llm_findings: List[Dict[str, Any]] = []

    def review_directory(self, target_path: str) -> List[SecurityFinding]:
        """
        Review selected risky files from the target directory.
        """

        target = Path(target_path)

        if not target.exists():
            raise FileNotFoundError(f"Target path does not exist: {target_path}")

        selected_files = self._select_files_for_review(target)

        findings: List[SecurityFinding] = []

        for file_path in selected_files:
            findings.extend(self.review_file(file_path))

        return findings

    def review_file(self, file_path: Path) -> List[SecurityFinding]:
        """
        Review a single file using Ollama.
        """

        try:
            code = file_path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            code = file_path.read_text(encoding="latin-1")

        code = code[: self.MAX_CHARS_PER_FILE]

        prompt = self._build_prompt(
            file_path=str(file_path),
            code=code
        )

        try:
            llm_output = self.llm_provider.generate(prompt)
            parsed_items = self._parse_llm_json(llm_output)
        except Exception as error:
            parsed_items = [
                {
                    "title": "LLM review failed",
                    "description": f"The LLM review failed for this file: {error}",
                    "severity": "Low",
                    "line": 0,
                    "cwe": "N/A",
                    "recommendation": "Check Ollama availability and retry the LLM review.",
                    "confidence": 0.0
                }
            ]

        findings: List[SecurityFinding] = []

        for item in parsed_items:
            normalized = self._normalize_llm_finding(item, str(file_path))
            self.llm_findings.append(normalized)

            findings.append(
                self.factory.create_finding(
                    title=normalized["title"],
                    description=normalized["description"],
                    severity=normalized["severity"],
                    file=str(file_path),
                    line=normalized["line"],
                    detection_method="LLM",
                    cwe=normalized["cwe"],
                    recommendation=normalized["recommendation"]
                )
            )

        return findings

    def _select_files_for_review(self, target: Path) -> List[Path]:
        """
        Select files that are most useful for security review.

        Priority:
        - app.py
        - files containing auth, checkout, cart, order, payment
        - frontend files
        """

        candidate_files: List[Path] = []

        for file_path in target.rglob("*"):
            if not file_path.is_file():
                continue

            if file_path.suffix.lower() not in self.SUPPORTED_EXTENSIONS:
                continue

            candidate_files.append(file_path)

        def priority(file_path: Path) -> int:
            name = file_path.name.lower()
            full_path = str(file_path).lower()

            if name == "app.py":
                return 0

            high_value_terms = [
                "auth",
                "login",
                "checkout",
                "cart",
                "order",
                "payment",
                "admin"
            ]

            if any(term in full_path for term in high_value_terms):
                return 1

            if file_path.suffix.lower() in [".js", ".jsx", ".ts", ".tsx"]:
                return 2

            return 3

        candidate_files.sort(key=priority)

        return candidate_files[: self.MAX_FILES_TO_REVIEW]

    def _build_prompt(self, file_path: str, code: str) -> str:
        """
        Build strict JSON prompt for Ollama.
        """

        return f"""
You are the LLM-assisted secure code reviewer for AutoForge.

Project domain:
E-commerce web application with catalog, cart, checkout, and order modules.

Task:
Review the following source code for security risks.

Return ONLY valid JSON.
Do not include markdown.
Do not include explanations outside JSON.
Do not wrap JSON in ```json blocks.

Output format:
{{
  "findings": [
    {{
      "title": "short finding title",
      "description": "clear security risk explanation",
      "severity": "Critical | High | Medium | Low",
      "line": 0,
      "cwe": "CWE-ID or N/A",
      "recommendation": "specific fix recommendation",
      "confidence": 0.0
    }}
  ]
}}

Rules:
- Only report realistic security risks.
- Avoid duplicate findings already obvious from simple syntax unless useful.
- Prefer authentication, authorization, input validation, checkout, order, cart, payment, secret, and injection risks.
- Use line number 0 if unsure.
- Severity must be exactly one of: Critical, High, Medium, Low.
- confidence must be between 0.0 and 1.0.
- If no issue is found, return:
{{
  "findings": []
}}

File path:
{file_path}

Code:
{code}
"""

    def _parse_llm_json(self, llm_output: str) -> List[Dict[str, Any]]:
        """
        Safely parse JSON from LLM output.

        Ollama may sometimes return extra text, so this method extracts
        the first JSON object from the response.
        """

        try:
            data = json.loads(llm_output)
        except json.JSONDecodeError:
            match = re.search(r"\{.*\}", llm_output, re.DOTALL)

            if not match:
                raise ValueError("No JSON object found in LLM output.")

            data = json.loads(match.group(0))

        findings = data.get("findings", [])

        if not isinstance(findings, list):
            raise ValueError("LLM output field 'findings' must be a list.")

        return findings

    def _normalize_llm_finding(
        self,
        item: Dict[str, Any],
        file_path: str
    ) -> Dict[str, Any]:
        """
        Normalize one LLM finding.
        """

        severity = str(item.get("severity", "Medium")).strip().capitalize()

        if severity not in ["Critical", "High", "Medium", "Low"]:
            severity = "Medium"

        try:
            line = int(item.get("line", 0))
        except ValueError:
            line = 0

        try:
            confidence = float(item.get("confidence", 0.5))
        except ValueError:
            confidence = 0.5

        confidence = max(0.0, min(confidence, 1.0))

        return {
            "title": str(item.get("title", "LLM security finding")),
            "description": str(item.get("description", "Security issue identified by LLM review.")),
            "severity": severity,
            "file": file_path,
            "line": line,
            "cwe": str(item.get("cwe", "N/A")),
            "recommendation": str(item.get("recommendation", "Review and fix the issue.")),
            "confidence": confidence,
            "source": "ollama"
        }