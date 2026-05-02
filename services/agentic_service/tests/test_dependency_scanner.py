from pathlib import Path

from agents.security_agent.scanners.base import FindingFactory
from agents.security_agent.scanners.dependency_scanner import DependencyScanner


def test_dependency_scanner_uses_mock_fallback_for_requirements(tmp_path: Path):
    """
    Checks that the dependency scanner can detect vulnerable Python packages
    using the mock fallback database when OSV is disabled.
    """

    requirements_file = tmp_path / "requirements.txt"
    requirements_file.write_text(
        "django==1.2\nflask==0.12\nfastapi==0.110.0\n",
        encoding="utf-8"
    )

    scanner = DependencyScanner(
        factory=FindingFactory(),
        use_osv=False
    )

    findings = scanner.scan_directory(str(tmp_path))

    titles = [finding.title for finding in findings]

    assert "Vulnerable dependency detected: django" in titles
    assert "Vulnerable dependency detected: flask" in titles
    assert "Vulnerable dependency detected: fastapi" not in titles


def test_dependency_scanner_uses_mock_fallback_for_package_json(tmp_path: Path):
    """
    Checks that the dependency scanner can detect vulnerable npm packages
    using the mock fallback database when OSV is disabled.
    """

    package_file = tmp_path / "package.json"
    package_file.write_text(
        """
{
  "name": "test-app",
  "dependencies": {
    "lodash": "4.17.15",
    "axios": "0.18.0",
    "react": "18.2.0"
  }
}
""",
        encoding="utf-8"
    )

    scanner = DependencyScanner(
        factory=FindingFactory(),
        use_osv=False
    )

    findings = scanner.scan_directory(str(tmp_path))

    titles = [finding.title for finding in findings]

    assert "Vulnerable dependency detected: lodash" in titles
    assert "Vulnerable dependency detected: axios" in titles
    assert "Vulnerable dependency detected: react" not in titles


def test_dependency_scanner_limits_vulnerabilities_per_package():
    """
    Checks Step 6.1 behavior:
    - deduplicate vulnerability records
    - sort by severity
    - limit max vulnerabilities per package
    """

    scanner = DependencyScanner(
        factory=FindingFactory(),
        use_osv=False
    )

    records = [
        {
            "id": "VULN-001",
            "severity": "Low",
            "cwe": "CWE-1",
            "description": "Low issue",
            "recommendation": "Fix low",
            "source": "test"
        },
        {
            "id": "VULN-002",
            "severity": "Critical",
            "cwe": "CWE-2",
            "description": "Critical issue",
            "recommendation": "Fix critical",
            "source": "test"
        },
        {
            "id": "VULN-003",
            "severity": "High",
            "cwe": "CWE-3",
            "description": "High issue",
            "recommendation": "Fix high",
            "source": "test"
        },
        {
            "id": "VULN-004",
            "severity": "Medium",
            "cwe": "CWE-4",
            "description": "Medium issue",
            "recommendation": "Fix medium",
            "source": "test"
        },
        {
            "id": "VULN-005",
            "severity": "High",
            "cwe": "CWE-5",
            "description": "High issue 2",
            "recommendation": "Fix high 2",
            "source": "test"
        },
        {
            "id": "VULN-006",
            "severity": "Medium",
            "cwe": "CWE-6",
            "description": "Medium issue 2",
            "recommendation": "Fix medium 2",
            "source": "test"
        },
        {
            "id": "VULN-002",
            "severity": "Critical",
            "cwe": "CWE-2",
            "description": "Duplicate critical issue",
            "recommendation": "Fix duplicate",
            "source": "test"
        }
    ]

    cleaned = scanner._deduplicate_sort_and_limit(records)

    assert len(cleaned) == scanner.MAX_VULNERABILITIES_PER_PACKAGE
    assert cleaned[0]["severity"] == "Critical"

    ids = [item["id"] for item in cleaned]
    assert ids.count("VULN-002") == 1