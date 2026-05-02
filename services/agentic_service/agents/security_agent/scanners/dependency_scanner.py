import json
import re
from pathlib import Path
from typing import List, Dict, Any, Optional

import httpx

from agents.security_agent.schemas import SecurityFinding
from agents.security_agent.scanners.base import FindingFactory


class DependencyScanner:
    """
    Dependency scanner for Python and Node.js dependency files.

    Scans:
    - requirements.txt
    - package.json

    Step 5:
    - Mock vulnerability database.

    Step 6:
    - Real OSV.dev API lookup.

    Step 6.1:
    - Deduplicate vulnerability results.
    - Sort by severity.
    - Limit the maximum number of vulnerabilities per package.

    Supported ecosystems:
    - PyPI for Python requirements.txt
    - npm for package.json
    """

    OSV_QUERY_URL = "https://api.osv.dev/v1/query"

    # Keep the report readable.
    # For very old packages like django==1.2, OSV may return many historical vulnerabilities.
    MAX_VULNERABILITIES_PER_PACKAGE = 5

    SEVERITY_RANK = {
        "Critical": 4,
        "High": 3,
        "Medium": 2,
        "Low": 1
    }

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

    def __init__(self, factory: FindingFactory, use_osv: bool = True):
        self.factory = factory
        self.use_osv = use_osv
        self.dependency_vulnerabilities: List[Dict[str, Any]] = []

    def scan_directory(self, target_path: str) -> List[SecurityFinding]:
        """
        Scan dependency manifest files inside the target project.
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
        Scan Python requirements.txt file and check dependencies against OSV.dev.
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

            if not package_name or not version:
                continue

            vulnerability_records = self._lookup_vulnerabilities(
                package_name=package_name,
                version=version,
                ecosystem="PyPI"
            )

            for vulnerability in vulnerability_records:
                findings.append(
                    self._create_dependency_finding(
                        package_name=package_name,
                        version=version,
                        vulnerability=vulnerability,
                        file_path=file_path,
                        line_number=line_number,
                        ecosystem="PyPI"
                    )
                )

        return findings

    def scan_package_json(self, file_path: Path) -> List[SecurityFinding]:
        """
        Scan Node.js package.json file and check dependencies against OSV.dev.
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

            if not clean_version:
                continue

            vulnerability_records = self._lookup_vulnerabilities(
                package_name=package_name,
                version=clean_version,
                ecosystem="npm"
            )

            for vulnerability in vulnerability_records:
                findings.append(
                    self._create_dependency_finding(
                        package_name=package_name,
                        version=clean_version,
                        vulnerability=vulnerability,
                        file_path=file_path,
                        line_number=0,
                        ecosystem="npm"
                    )
                )

        return findings

    def _lookup_vulnerabilities(
        self,
        package_name: str,
        version: str,
        ecosystem: str
    ) -> List[Dict[str, Any]]:
        """
        Query OSV.dev first.

        If OSV.dev is unavailable or returns an error, use mock fallback.

        Step 6.1 improvement:
        - Deduplicate results.
        - Sort by severity.
        - Limit to top N vulnerabilities per package.
        """

        vulnerability_records: List[Dict[str, Any]] = []

        if self.use_osv:
            try:
                vulnerability_records = self._query_osv(
                    package_name=package_name,
                    version=version,
                    ecosystem=ecosystem
                )
            except Exception:
                # Fallback is intentional for MVP stability.
                vulnerability_records = []

        if not vulnerability_records:
            mock_result = self._check_mock_vulnerability(package_name, version)

            if mock_result:
                vulnerability_records = [mock_result]

        cleaned_results = self._deduplicate_sort_and_limit(vulnerability_records)

        return cleaned_results

    def _query_osv(
        self,
        package_name: str,
        version: str,
        ecosystem: str
    ) -> List[Dict[str, Any]]:
        """
        Query OSV.dev /v1/query endpoint.

        Request body example:
        {
          "version": "4.17.15",
          "package": {
            "name": "lodash",
            "ecosystem": "npm"
          }
        }
        """

        payload = {
            "version": version,
            "package": {
                "name": package_name,
                "ecosystem": ecosystem
            }
        }

        with httpx.Client(timeout=15) as client:
            response = client.post(self.OSV_QUERY_URL, json=payload)
            response.raise_for_status()
            data = response.json()

        vulns = data.get("vulns", [])
        normalized_results: List[Dict[str, Any]] = []

        for vuln in vulns:
            normalized_results.append(
                {
                    "id": vuln.get("id", "UNKNOWN"),
                    "severity": self._extract_severity(vuln),
                    "cwe": self._extract_cwe(vuln),
                    "description": vuln.get("summary")
                    or vuln.get("details")
                    or "Vulnerability found in OSV.dev.",
                    "recommendation": self._build_osv_recommendation(vuln),
                    "source": "osv.dev",
                    "raw": {
                        "modified": vuln.get("modified", ""),
                        "published": vuln.get("published", ""),
                        "aliases": vuln.get("aliases", [])
                    }
                }
            )

        return normalized_results

    def _deduplicate_sort_and_limit(
        self,
        vulnerability_records: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Clean OSV results.

        1. Deduplicate by vulnerability ID.
        2. Sort by severity: Critical > High > Medium > Low.
        3. Keep only top MAX_VULNERABILITIES_PER_PACKAGE records.

        This keeps the report readable and reduces noise.
        """

        unique_records: Dict[str, Dict[str, Any]] = {}

        for record in vulnerability_records:
            vuln_id = record.get("id", "UNKNOWN")

            if vuln_id not in unique_records:
                unique_records[vuln_id] = record

        sorted_records = sorted(
            unique_records.values(),
            key=lambda item: self.SEVERITY_RANK.get(item.get("severity", "Medium"), 2),
            reverse=True
        )

        return sorted_records[: self.MAX_VULNERABILITIES_PER_PACKAGE]

    def _parse_python_requirement(self, line: str) -> tuple[str, str]:
        """
        Parse Python dependency line.

        Examples:
        django==1.2
        flask==0.12
        requests>=2.19.0

        For the MVP, exact versions work best.
        """

        match = re.match(
            r"^([A-Za-z0-9_.-]+)\s*(==|>=|<=|~=|>|<)?\s*([A-Za-z0-9_.-]+)?",
            line
        )

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

        return (
            version
            .replace("^", "")
            .replace("~", "")
            .replace(">=", "")
            .replace("<=", "")
            .replace(">", "")
            .replace("<", "")
            .strip()
        )

    def _check_mock_vulnerability(
        self,
        package_name: str,
        version: str
    ) -> Optional[Dict[str, Any]]:
        """
        Check dependency against mock vulnerability database.
        Used only as fallback or offline mode.
        """

        package_name = package_name.lower()

        vulnerability = self.MOCK_VULNERABLE_PACKAGES.get(package_name)

        if not vulnerability:
            return None

        if version in vulnerability["vulnerable_versions"]:
            return {
                "id": f"MOCK-{package_name.upper()}-{version}",
                "severity": vulnerability["severity"],
                "cwe": vulnerability["cwe"],
                "description": vulnerability["description"],
                "recommendation": vulnerability["recommendation"],
                "source": "mock",
                "raw": {}
            }

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
            "id": vulnerability.get("id", "UNKNOWN"),
            "package": package_name,
            "version": version,
            "ecosystem": ecosystem,
            "severity": vulnerability.get("severity", "Medium"),
            "cwe": vulnerability.get("cwe", "CWE-937"),
            "description": vulnerability.get("description", "Dependency vulnerability detected."),
            "recommendation": vulnerability.get("recommendation", "Upgrade the dependency to a secure version."),
            "source": vulnerability.get("source", "unknown")
        }

        self.dependency_vulnerabilities.append(vuln_record)

        return self.factory.create_finding(
            title=f"Vulnerable dependency detected: {package_name}",
            description=(
                f"{vuln_record['description']} "
                f"Package: {package_name}, Version: {version}, Ecosystem: {ecosystem}, "
                f"Vulnerability ID: {vuln_record['id']}."
            ),
            severity=vuln_record["severity"],
            file=str(file_path),
            line=line_number,
            detection_method="Dependency",
            cwe=vuln_record["cwe"],
            recommendation=vuln_record["recommendation"]
        )

    def _extract_severity(self, vuln: Dict[str, Any]) -> str:
        """
        Extract and normalize severity from OSV vulnerability object.

        OSV records may not always contain a direct severity label.
        """

        database_specific = vuln.get("database_specific", {})

        severity = database_specific.get("severity")

        if severity:
            severity = str(severity).capitalize()

            if severity in ["Critical", "High", "Medium", "Low"]:
                return severity

        severity_items = vuln.get("severity", [])

        for item in severity_items:
            score = str(item.get("score", "")).upper()

            if "CVSS" in score:
                return self._severity_from_cvss_vector(score)

        return "Medium"

    def _severity_from_cvss_vector(self, score: str) -> str:
        """
        Simple CVSS vector-based fallback.

        This is not a full CVSS calculator, but it improves severity sorting
        when OSV does not provide a direct severity label.
        """

        if "/AV:N" in score and "/I:H" in score and "/A:H" in score:
            return "Critical"

        if "/AV:N" in score and ("/I:H" in score or "/A:H" in score):
            return "High"

        if "/AV:N" in score:
            return "Medium"

        return "Low"

    def _extract_cwe(self, vuln: Dict[str, Any]) -> str:
        """
        Extract CWE from OSV aliases or database_specific fields when available.
        """

        aliases = vuln.get("aliases", [])

        for alias in aliases:
            if str(alias).startswith("CWE-"):
                return alias

        database_specific = vuln.get("database_specific", {})
        cwe_ids = database_specific.get("cwe_ids", [])

        if cwe_ids:
            return cwe_ids[0]

        return "CWE-937"

    def _build_osv_recommendation(self, vuln: Dict[str, Any]) -> str:
        """
        Build a simple recommendation from OSV data.
        """

        vuln_id = vuln.get("id", "the reported vulnerability")

        return (
            f"Review {vuln_id} in OSV.dev and upgrade the affected dependency "
            f"to a patched or currently supported version."
        )