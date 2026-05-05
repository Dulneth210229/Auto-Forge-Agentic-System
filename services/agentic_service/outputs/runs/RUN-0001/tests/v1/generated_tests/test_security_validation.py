import json
from pathlib import Path

import pytest


SECURITY_REPORT_PATH = Path(r"outputs\runs\RUN-0001\security\v1\SecurityReport_v1.json")


def _load_security_report() -> dict:
    if not SECURITY_REPORT_PATH.exists():
        pytest.skip(f"Security report not found: {SECURITY_REPORT_PATH}")

    return json.loads(SECURITY_REPORT_PATH.read_text(encoding="utf-8"))


def test_security_report_json_exists():
    if not SECURITY_REPORT_PATH.exists():
        pytest.skip(f"Security report not found: {SECURITY_REPORT_PATH}")

    assert SECURITY_REPORT_PATH.exists()


def test_security_report_has_required_top_level_sections():
    report = _load_security_report()

    required_sections = [
        "run_id",
        "stage",
        "version",
        "summary",
        "findings",
        "security_gate",
        "metrics"
    ]

    for section in required_sections:
        assert section in report, f"Missing SecurityReport section: {section}"


def test_security_gate_has_valid_structure():
    report = _load_security_report()

    gate = report.get("security_gate", {})

    assert gate.get("status") in ["PASS", "WARN", "FAIL"]
    assert isinstance(gate.get("reason", ""), str)
    assert isinstance(gate.get("policy", ""), str)
    assert isinstance(gate.get("blocking_findings", []), list)


def test_security_findings_have_required_fields():
    report = _load_security_report()

    findings = report.get("findings", [])

    for finding in findings:
        assert finding.get("finding_id"), "Finding is missing finding_id."
        assert finding.get("title"), "Finding is missing title."
        assert finding.get("severity") in ["Critical", "High", "Medium", "Low"]
        assert "file" in finding
        assert "recommendation" in finding


def test_security_fix_suggestions_reference_existing_findings():
    report = _load_security_report()

    findings = report.get("findings", [])
    fix_suggestions = report.get("fix_suggestions", [])

    finding_ids = {
        finding.get("finding_id")
        for finding in findings
        if finding.get("finding_id")
    }

    for fix in fix_suggestions:
        assert fix.get("finding_id") in finding_ids, (
            f"Fix suggestion references unknown finding: {fix.get('finding_id')}"
        )


def test_security_findings_have_traceability_fields():
    report = _load_security_report()

    findings = report.get("findings", [])

    for finding in findings:
        traceability = finding.get("traceability", {})

        assert "requirement_id" in traceability
        assert "api" in traceability
        assert "module" in traceability


def test_security_summary_matches_findings_count():
    report = _load_security_report()

    summary = report.get("summary", {})
    findings = report.get("findings", [])

    assert summary.get("total_findings", 0) == len(findings)
