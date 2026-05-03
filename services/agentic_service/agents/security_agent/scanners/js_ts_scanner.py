import re
from pathlib import Path
from typing import List

from agents.security_agent.schemas import SecurityFinding
from agents.security_agent.scanners.base import FindingFactory


class JSTypescriptScanner:
    """
    Pattern-based scanner for JavaScript, TypeScript, and React files.

    Scans:
    - .js
    - .jsx
    - .ts
    - .tsx

    Detects common frontend/backend JavaScript security risks.
    """

    SUPPORTED_EXTENSIONS = {".js", ".jsx", ".ts", ".tsx"}

    def __init__(self, factory: FindingFactory):
        self.factory = factory

    def scan_directory(self, target_path: str) -> List[SecurityFinding]:
        target = Path(target_path)
        findings: List[SecurityFinding] = []

        for file_path in target.rglob("*"):
            if file_path.is_file() and file_path.suffix.lower() in self.SUPPORTED_EXTENSIONS:
                findings.extend(self.scan_file(file_path))

        return findings

    def scan_file(self, file_path: Path) -> List[SecurityFinding]:
        findings: List[SecurityFinding] = []

        try:
            source_code = file_path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            source_code = file_path.read_text(encoding="latin-1")

        lines = source_code.splitlines()

        for line_number, line in enumerate(lines, start=1):
            stripped = line.strip()

            if re.search(r"\beval\s*\(", stripped):
                findings.append(
                    self.factory.create_finding(
                        title="JavaScript eval() usage detected",
                        description="JavaScript eval() can execute arbitrary code and may lead to code injection.",
                        severity="Critical",
                        file=str(file_path),
                        line=line_number,
                        detection_method="AST",
                        cwe="CWE-95",
                        recommendation="Avoid eval(). Use safe parsing or explicit logic instead."
                    )
                )

            if "dangerouslySetInnerHTML" in stripped:
                findings.append(
                    self.factory.create_finding(
                        title="React dangerouslySetInnerHTML usage detected",
                        description="dangerouslySetInnerHTML may introduce XSS if user input is rendered without sanitization.",
                        severity="High",
                        file=str(file_path),
                        line=line_number,
                        detection_method="AST",
                        cwe="CWE-79",
                        recommendation="Avoid dangerouslySetInnerHTML or sanitize HTML using a trusted sanitizer."
                    )
                )

            if ".innerHTML" in stripped:
                findings.append(
                    self.factory.create_finding(
                        title="Direct innerHTML assignment detected",
                        description="Assigning content to innerHTML may introduce XSS if the content includes user input.",
                        severity="High",
                        file=str(file_path),
                        line=line_number,
                        detection_method="AST",
                        cwe="CWE-79",
                        recommendation="Use textContent or sanitize HTML before assigning it to the DOM."
                    )
                )

            if "localStorage.setItem" in stripped and re.search(r"token|jwt|secret|auth", stripped, re.IGNORECASE):
                findings.append(
                    self.factory.create_finding(
                        title="Sensitive token stored in localStorage",
                        description="Storing authentication tokens in localStorage can increase exposure to XSS attacks.",
                        severity="Medium",
                        file=str(file_path),
                        line=line_number,
                        detection_method="AST",
                        cwe="CWE-922",
                        recommendation="Prefer secure, HttpOnly cookies for sensitive session tokens."
                    )
                )

            if re.search(r"child_process\.(exec|execSync)\s*\(", stripped):
                findings.append(
                    self.factory.create_finding(
                        title="Unsafe Node.js command execution detected",
                        description="child_process.exec can lead to command injection if input is user-controlled.",
                        severity="High",
                        file=str(file_path),
                        line=line_number,
                        detection_method="AST",
                        cwe="CWE-78",
                        recommendation="Avoid exec with user input. Use safer APIs and strict input validation."
                    )
                )

            if re.search(r"console\.log\s*\(.*(password|token|secret|api_key|apikey)", stripped, re.IGNORECASE):
                findings.append(
                    self.factory.create_finding(
                        title="Sensitive data logged to console",
                        description="Logging secrets or tokens can expose sensitive information in logs.",
                        severity="Medium",
                        file=str(file_path),
                        line=line_number,
                        detection_method="AST",
                        cwe="CWE-532",
                        recommendation="Remove sensitive data from logs."
                    )
                )

        return findings