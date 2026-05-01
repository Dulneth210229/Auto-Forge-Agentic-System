from pathlib import Path
from typing import List, Dict, Any

from agents.security_agent.schemas import SecurityFinding
from agents.security_agent.scanners.base import FindingFactory
from agents.security_agent.scanners.python_ast_scanner import PythonASTScanner
from agents.security_agent.scanners.js_ts_scanner import JSTypescriptScanner
from agents.security_agent.scanners.secret_scanner import SecretScanner
from agents.security_agent.scanners.config_scanner import ConfigScanner
from agents.security_agent.scanners.dependency_scanner import DependencyScanner


class MultiSecurityScanner:
    """
    Runs all available security scanners on a target project folder.

    Current scanners:
    - PythonASTScanner
    - JSTypescriptScanner
    - SecretScanner
    - ConfigScanner
    - DependencyScanner
    """

    def __init__(self):
        self.factory = FindingFactory()

        self.dependency_scanner = DependencyScanner(self.factory)

        self.scanners = [
            PythonASTScanner(self.factory),
            JSTypescriptScanner(self.factory),
            SecretScanner(self.factory),
            ConfigScanner(self.factory),
            self.dependency_scanner
        ]

    def scan_directory(self, target_path: str) -> List[SecurityFinding]:
        target = Path(target_path)

        if not target.exists():
            raise FileNotFoundError(f"Target path does not exist: {target_path}")

        findings: List[SecurityFinding] = []

        for scanner in self.scanners:
            findings.extend(scanner.scan_directory(target_path))

        return findings

    def get_dependency_vulnerabilities(self) -> List[Dict[str, Any]]:
        """
        Return normalized dependency vulnerability records.
        These will be stored separately in SecurityReport_v1.json.
        """

        return self.dependency_scanner.dependency_vulnerabilities