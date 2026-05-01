import json
import re
from pathlib import Path
from typing import List, Dict, Any

from agents.security_agent.schemas import SecurityFinding
from agents.security_agent.scanners.base import FindingFactory


class DependencyScanner:
    """
    Dependency scanner for Python and Node.js dependency files.

    Scans:
    - requirements.txt
    - package.json

    Current MVP:
    - Uses a mock vulnerability database.
    - Later this can be replaced or extended with OSV.dev, pip-audit, or npm audit.
    """

    MOCK_VULNERABLE_PACKAGES = {
        "django": {
            "vulnerable_versions": ["1.2", "1.8", "2.0"],
            "severity": "High",
            "cwe": "CWE-937",
            "description": "Known vulnerable Django version detected.",
            "recommendation": "Upgrade Django to a currently supported secure version."
        },
        "flask": {
            "vulnerable_versions": ["0.12", "1.0"],
            "severity": "Medium",
            "cwe": "CWE-937",
            "description": "Outdated Flask version detected.",
            "recommendation": "Upgrade Flask to the latest stable version."
        },
        "requests": {
            "vulnerable_versions": ["2.19.0", "2.20.0"],
            "severity": "Medium",
            "cwe": "CWE-937",
            "description": "Outdated requests package detected.",
            "recommendation": "Upgrade requests to a newer secure version."
        },
        "lodash": {
            "vulnerable_versions": ["4.17.15", "4.17.19"],
            "severity": "High",
            "cwe": "CWE-400",
            "description": "Known vulnerable lodash version detected.",
            "recommendation": "Upgrade lodash to version 4.17.21 or later."
        },
        "express": {
            "vulnerable_versions": ["3.0.0", "4.16.0"],
            "severity": "Medium",
            "cwe": "CWE-937",
            "description": "Outdated Express version detected.",
            "recommendation": "Upgrade Express to a newer secure version."
        },
        "axios": {
            "vulnerable_versions": ["0.18.0", "0.19.0"],
            "severity": "High",
            "cwe": "CWE-918",
            "description": "Known vulnerable axios version detected.",
            "recommendation": "Upgrade axios to a newer secure version."
        }
    }

    def __init__(self, factory: FindingFactory):
        self.factory = factory
        self.dependency_vulnerabilities: List[Dict[str, Any]] = []

    def scan_directory(self, target_path: str) -> List[SecurityFinding]:
        """
        Scan dependency files inside the target project.
        """

        target = Path(target_path)
        findings: List[SecurityFinding] = []

        for file_path in target.rglob("*"):
            if not file_path.is_file():
                continue

            if file_path.name == "requirements.txt":
                findings.extend(self.scan_requirements_txt(file_path))

            if file_path.name == "package.json":
                findings.extend(self.scan_package_json(file_path))

        return findings

    def scan_requirements_txt(self, file_path: Path) -> List[SecurityFinding]:
        """
        Scan Python requirements.txt file.
        """

        findings: List[SecurityFinding] = []

        try:
            content = file_path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            content = file_path.read_text(encoding="latin-1")

        lines = content.splitlines()

        for line_number, line in enumerate(lines, start=1):
            line = line.strip()

            if not line or line.startswith("#"):
                continue

            package_name, version = self._parse_python_requirement(line)

            if not package_name:
                continue

            vulnerability = self._check_mock_vulnerability(package_name, version)

            if vulnerability:
                finding = self._create_dependency_finding(
                    package_name=package_name,
                    version=version,
                    vulnerability=vulnerability,
                    file_path=file_path,
                    line_number=line_number,
                    ecosystem="PyPI"
                )
                findings.append(finding)

        return findings

    def scan_package_json(self, file_path: Path) -> List[SecurityFinding]:
        """
        Scan Node.js package.json file.
        """

        findings: List[SecurityFinding] = []

        try:
            package_data = json.loads(file_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            findings.append(
                self.factory.create_finding(
                    title="Invalid package.json file",
                    description="The package.json file could not be parsed as valid JSON.",
                    severity="Low",
                    file=str(file_path),
                    line=0,
                    detection_method="Dependency",
                    cwe="N/A",
                    recommendation="Fix the package.json syntax so dependency scanning can run correctly."
                )
            )
            return findings

        dependencies = package_data.get("dependencies", {})
        dev_dependencies = package_data.get("devDependencies", {})

        all_dependencies = {}
        all_dependencies.update(dependencies)
        all_dependencies.update(dev_dependencies)

        for package_name, version in all_dependencies.items():
            clean_version = self._clean_node_version(str(version))
            vulnerability = self._check_mock_vulnerability(package_name, clean_version)

            if vulnerability:
                finding = self._create_dependency_finding(
                    package_name=package_name,
                    version=clean_version,
                    vulnerability=vulnerability,
                    file_path=file_path,
                    line_number=0,
                    ecosystem="npm"
                )
                findings.append(finding)

        return findings

    def _parse_python_requirement(self, line: str) -> tuple[str, str]:
        """
        Parse Python dependency line.

        Examples:
        django==1.2
        flask==0.12
        requests>=2.19.0
        """

        match = re.match(r"^([A-Za-z0-9_.-]+)\s*(==|>=|<=|~=|>|<)?\s*([A-Za-z0-9_.-]+)?", line)

        if not match:
            return "", ""

        package_name = match.group(1).lower()
        version = match.group(3) or ""

        return package_name, version

    def _clean_node_version(self, version: str) -> str:
        """
        Remove npm version prefix characters.

        Examples:
        ^4.17.15 → 4.17.15
        ~0.18.0 → 0.18.0
        """

        return version.replace("^", "").replace("~", "").replace(">=", "").replace("<=", "").strip()

    def _check_mock_vulnerability(self, package_name: str, version: str) -> Dict[str, Any] | None:
        """
        Check dependency against mock vulnerability database.
        """

        package_name = package_name.lower()

        vulnerability = self.MOCK_VULNERABLE_PACKAGES.get(package_name)

        if not vulnerability:
            return None

        if version in vulnerability["vulnerable_versions"]:
            return vulnerability

        return None

    def _create_dependency_finding(
        self,
        package_name: str,
        version: str,
        vulnerability: Dict[str, Any],
        file_path: Path,
        line_number: int,
        ecosystem: str
    ) -> SecurityFinding:
        """
        Create SecurityFinding and store normalized dependency vulnerability data.
        """

        vuln_record = {
            "package": package_name,
            "version": version,
            "ecosystem": ecosystem,
            "severity": vulnerability["severity"],
            "description": vulnerability["description"],
            "recommendation": vulnerability["recommendation"],
            "source": "mock"
        }

        self.dependency_vulnerabilities.append(vuln_record)

        return self.factory.create_finding(
            title=f"Vulnerable dependency detected: {package_name}",
            description=f"{vulnerability['description']} Package: {package_name}, Version: {version}, Ecosystem: {ecosystem}.",
            severity=vulnerability["severity"],
            file=str(file_path),
            line=line_number,
            detection_method="Dependency",
            cwe=vulnerability["cwe"],
            recommendation=vulnerability["recommendation"]
        )