from agents.security_agent.schemas import (
    SecurityReport,
    SecuritySummary,
    SecurityFinding,
    TraceabilityLink,
    SecurityMetrics
)
from agents.security_agent.renderer import render_security_report_markdown


def test_security_report_markdown_rendering():
    """
    This test checks whether JSON SecurityReport data can be rendered into Markdown.
    """

    finding = SecurityFinding(
        finding_id="SEC-001",
        title="Use of eval() detected",
        description="eval() can execute arbitrary code.",
        severity="Critical",
        file="sample_ecommerce_app/app.py",
        line=25,
        detection_method="AST",
        cwe="CWE-95",
        recommendation="Avoid eval(). Use safe parsing instead.",
        traceability=TraceabilityLink(
            requirement_id="FR-003",
            api="/api/search",
            module="catalog"
        )
    )

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
        metrics=SecurityMetrics(
            coverage=1.0,
            confidence=0.8
        )
    )

    markdown = render_security_report_markdown(report)

    assert "# Security Report" in markdown
    assert "RUN-0001" in markdown
    assert "SEC-001" in markdown
    assert "Use of eval() detected" in markdown
    assert "Critical" in markdown