import re
from pathlib import Path
from typing import List

from agents.security_agent.schemas import SecurityFinding
from agents.security_agent.scanners.base import FindingFactory


class ConfigScanner:
    """
    Scanner for configuration and deployment files.

    Scans:
    - .env
    - Dockerfile
    - docker-compose.yml
    - docker-compose.yaml
    - config.yml / config.yaml / config.json
    """

    CONFIG_FILE_NAMES = {
        ".env",
        "Dockerfile",
        "docker-compose.yml",
        "docker-compose.yaml",
        "config.yml",
        "config.yaml",
        "config.json"
    }

    def __init__(self, factory: FindingFactory):
        self.factory = factory

    def scan_directory(self, target_path: str) -> List[SecurityFinding]:
        target = Path(target_path)
        findings: List[SecurityFinding] = []

        for file_path in target.rglob("*"):
            if file_path.is_file() and file_path.name in self.CONFIG_FILE_NAMES:
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
            stripped = line.strip()

            if re.search(r"(?i)debug\s*[:=]\s*(true|1|yes)", stripped):
                findings.append(
                    self.factory.create_finding(
                        title="Debug configuration enabled",
                        description="Debug mode appears to be enabled in a configuration file.",
                        severity="Medium",
                        file=str(file_path),
                        line=line_number,
                        detection_method="AST",
                        cwe="CWE-489",
                        recommendation="Disable debug mode in production configurations."
                    )
                )

            if file_path.name == "Dockerfile" and re.search(r"USER\s+root", stripped):
                findings.append(
                    self.factory.create_finding(
                        title="Docker container runs as root",
                        description="Running containers as root increases the impact of container compromise.",
                        severity="Medium",
                        file=str(file_path),
                        line=line_number,
                        detection_method="AST",
                        cwe="CWE-250",
                        recommendation="Create and use a non-root user inside the Docker image."
                    )
                )

            if re.search(r"(?i)0\.0\.0\.0", stripped):
                findings.append(
                    self.factory.create_finding(
                        title="Service binds to all network interfaces",
                        description="Binding to 0.0.0.0 may expose the service externally if network controls are not configured.",
                        severity="Low",
                        file=str(file_path),
                        line=line_number,
                        detection_method="AST",
                        cwe="CWE-200",
                        recommendation="Use restricted host binding for local-only services where appropriate."
                    )
                )

            if re.search(r"(?i)(allow_origins|cors).*\*", stripped):
                findings.append(
                    self.factory.create_finding(
                        title="Wildcard CORS setting in configuration",
                        description="Wildcard CORS configuration may allow untrusted origins to interact with the application.",
                        severity="Medium",
                        file=str(file_path),
                        line=line_number,
                        detection_method="AST",
                        cwe="CWE-942",
                        recommendation="Restrict CORS settings to trusted frontend origins."
                    )
                )

        return findings