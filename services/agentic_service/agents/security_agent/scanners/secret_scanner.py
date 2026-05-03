import re
from pathlib import Path
from typing import List

from agents.security_agent.schemas import SecurityFinding
from agents.security_agent.scanners.base import FindingFactory


class SecretScanner:
    """
    Pattern-based secret scanner.

    This scanner checks common text-based files for hardcoded secrets.
    """

    SUPPORTED_EXTENSIONS = {
        ".py", ".js", ".jsx", ".ts", ".tsx",
        ".env", ".json", ".yml", ".yaml", ".txt"
    }

    SECRET_PATTERNS = [
        r"(?i)(api[_-]?key|apikey)\s*[:=]\s*[\"'][^\"']{4,}[\"']",
        r"(?i)(secret[_-]?key|secret|jwt[_-]?secret)\s*[:=]\s*[\"'][^\"']{4,}[\"']",
        r"(?i)(password|passwd|pwd|db_password)\s*[:=]\s*[\"'][^\"']{4,}[\"']",
        r"(?i)(access[_-]?token|auth[_-]?token|token)\s*[:=]\s*[\"'][^\"']{4,}[\"']",
        r"AKIA[0-9A-Z]{16}"
    ]

    def __init__(self, factory: FindingFactory):
        self.factory = factory

    def scan_directory(self, target_path: str) -> List[SecurityFinding]:
        target = Path(target_path)
        findings: List[SecurityFinding] = []

        for file_path in target.rglob("*"):
            if not file_path.is_file():
                continue

            if file_path.suffix.lower() in self.SUPPORTED_EXTENSIONS or file_path.name == ".env":
                findings.extend(self.scan_file(file_path))

        return findings

    def scan_file(self, file_path: Path) -> List[SecurityFinding]:
        findings: List[SecurityFinding] = []

        try:
            content = file_path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            content = file_path.read_text(encoding="latin-1")

        lines = content.splitlines()

        for line_number, line in enumerate(lines, start=1):
            for pattern in self.SECRET_PATTERNS:
                if re.search(pattern, line):
                    findings.append(
                        self.factory.create_finding(
                            title="Possible hardcoded secret detected",
                            description="A possible hardcoded secret, password, token, or API key was found in a text-based file.",
                            severity="High",
                            file=str(file_path),
                            line=line_number,
                            detection_method="AST",
                            cwe="CWE-798",
                            recommendation="Move secrets to environment variables or a dedicated secret manager."
                        )
                    )
                    break

        return findings