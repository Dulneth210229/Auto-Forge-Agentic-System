from agents.security_agent.summary_pack import (
    SecuritySummaryPackBuilder,
    SecuritySummaryPackRenderer
)
from agents.security_agent.schemas import (
    SecurityReport,
    SecuritySummary,
    SecurityFinding,
    TraceabilityLink,
    SecurityMetrics,
    SecurityGateDecision,
    SecurityFixSuggestion
)


def make_finding():
    return SecurityFinding(
        finding_id="SEC-001",
        title="Use of eval() detected",
        description="eval can execute arbitrary code.",
        severity="Critical",
        file="sample_ecommerce_app/app.py",
        line=10,
        detection_method="AST",
        cwe="CWE-95",
        recommendation="Avoid eval().",
        traceability=TraceabilityLink(
            requirement_id="NFR-SEC-001",
            api="N/A",
            module="general_security"
        )
    )


def test_summary_pack_builder_creates_dashboard_summary():
    finding = make_finding()

    report = SecurityReport(
        run_id="RUN-0001",
        stage="security",
        version="v1",
        summary=SecuritySummary(
            total_findings=1,
            critical=1,
            high=0,
            medium=0,
            low=0
        ),
        findings=[finding],
        dependency_vulnerabilities=[],
        llm_findings=[],
        security_gate=SecurityGateDecision(
            status="FAIL",
            reason="Critical vulnerabilities detected.",
            policy="FAIL if Critical findings exist.",
            blocking_findings=["SEC-001"]
        ),
        fix_suggestions=[
            SecurityFixSuggestion(
                finding_id="SEC-001",
                issue="Use of eval() detected",
                severity="Critical",
                file="sample_ecommerce_app/app.py",
                recommended_fix="Remove eval usage.",
                example_fix="Use json.loads instead.",
                priority="Immediate",
                effort="Medium"
            )
        ],
        metrics=SecurityMetrics(
            coverage=1.0,
            confidence=0.85
        )
    )

    builder = SecuritySummaryPackBuilder()

    pack = builder.build(
        report=report,
        json_report_path="SecurityReport_v1.json",
        markdown_report_path="SecurityReport_v1.md",
        deduplication_summary={
            "findings_before_deduplication": 2,
            "findings_after_deduplication": 1,
            "duplicates_removed": 1
        },
        target_path="./sample_ecommerce_app"
    )

    assert pack["run_id"] == "RUN-0001"
    assert pack["security_gate"]["status"] == "FAIL"
    assert pack["summary"]["total_findings"] == 1
    assert pack["counts"]["fix_suggestions"] == 1
    assert pack["traceability"]["coverage_percentage"] == 100.0
    assert len(pack["top_blocking_findings"]) == 1


def test_summary_pack_renderer_outputs_markdown():
    renderer = SecuritySummaryPackRenderer()

    pack = {
        "run_id": "RUN-0001",
        "stage": "security",
        "version": "v1",
        "generated_at": "2026-01-01T00:00:00+00:00",
        "target_path": "./sample_ecommerce_app",
        "security_gate": {
            "status": "FAIL",
            "reason": "Critical vulnerabilities detected.",
            "policy": "FAIL if Critical findings exist.",
            "blocking_findings": ["SEC-001"]
        },
        "summary": {
            "total_findings": 1,
            "critical": 1,
            "high": 0,
            "medium": 0,
            "low": 0
        },
        "metrics": {
            "coverage": 1.0,
            "confidence": 0.85
        },
        "deduplication": {
            "findings_before_deduplication": 2,
            "findings_after_deduplication": 1,
            "duplicates_removed": 1
        },
        "counts": {
            "total_findings": 1,
            "dependency_vulnerabilities": 0,
            "llm_findings": 0,
            "fix_suggestions": 1,
            "top_blocking_findings": 1
        },
        "traceability": {
            "coverage_percentage": 100.0,
            "mapped_findings": 1,
            "total_findings": 1
        },
        "top_blocking_findings": [
            {
                "finding_id": "SEC-001",
                "title": "Use of eval() detected",
                "severity": "Critical",
                "file": "sample_ecommerce_app/app.py",
                "line": 10,
                "detection_method": "AST",
                "cwe": "CWE-95",
                "requirement_id": "NFR-SEC-001",
                "api": "N/A",
                "module": "general_security",
                "recommendation": "Avoid eval()."
            }
        ],
        "artifacts": {
            "security_report_json": "SecurityReport_v1.json",
            "security_report_markdown": "SecurityReport_v1.md",
            "security_summary_pack_json": "SecuritySummaryPack_v1.json",
            "security_summary_pack_markdown": "SecuritySummaryPack_v1.md"
        }
    }

    markdown = renderer.render_markdown(pack)

    assert "# Security Summary Pack" in markdown
    assert "RUN-0001" in markdown
    assert "FAIL" in markdown
    assert "Use of eval() detected" in markdown
    assert "SecuritySummaryPack_v1.json" in markdown