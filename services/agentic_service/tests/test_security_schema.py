from agents.security_agent.schemas import (
    SecurityReport,
    SecuritySummary,
    SecurityFinding,
    TraceabilityLink,
    SecurityMetrics
)


def test_security_report_schema_validation():
    """
    This test checks whether SecurityReport follows the expected Pydantic schema.
    """

    finding = SecurityFinding(
        finding_id="SEC-001",
        title="Hardcoded secret detected",
        description="A hardcoded API key was found.",
        severity="High",
        file="sample_ecommerce_app/app.py",
        line=10,
        detection_method="AST",
        cwe="CWE-798",
        recommendation="Move secrets to environment variables.",
        traceability=TraceabilityLink(
            requirement_id="FR-004",
            api="/api/checkout",
            module="checkout"
        )
    )

    report = SecurityReport(
        run_id="RUN-0001",
        stage="security",
        version="v1",
        summary=SecuritySummary(
            total_findings=1,
            critical=0,
            high=1,
            medium=0,
            low=0
        ),
        findings=[finding],
        dependency_vulnerabilities=[],
        llm_findings=[],
        metrics=SecurityMetrics(
            coverage=1.0,
            confidence=0.8
        )
    )

    assert report.run_id == "RUN-0001"
    assert report.stage == "security"
    assert report.version == "v1"
    assert report.summary.total_findings == 1
    assert report.findings[0].finding_id == "SEC-001"