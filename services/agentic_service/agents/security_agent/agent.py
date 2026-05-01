import json
from pathlib import Path

from agents.security_agent.schemas import (
    SecurityReport,
    SecuritySummary,
    SecurityFinding,
    TraceabilityLink,
    SecurityMetrics
)
from agents.security_agent.renderer import render_security_report_markdown


class SecurityAgent:
    """
    Security Agent skeleton.

    Current responsibility:
    - Generate dummy SecurityReport_v1.json
    - Generate dummy SecurityReport_v1.md
    - Save both outputs under:
      outputs/runs/{run_id}/security/{version}/

    Real security scanning will be added in the next steps.
    """

    def __init__(self, output_root: str = "outputs"):
        self.output_root = Path(output_root)

    def create_dummy_report(self, run_id: str, version: str) -> SecurityReport:
        """
        Creates a dummy security report.

        This helps us test:
        - Pydantic schema validation
        - JSON output generation
        - Markdown rendering
        - Versioned folder structure
        """

        findings = [
            SecurityFinding(
                finding_id="SEC-001",
                title="Dummy hardcoded secret finding",
                description="This is dummy data. Real AST scanning will be added in the next step.",
                severity="High",
                file="sample_ecommerce_app/config.py",
                line=10,
                detection_method="AST",
                cwe="CWE-798",
                recommendation="Move secrets into environment variables and never commit them to source code.",
                traceability=TraceabilityLink(
                    requirement_id="FR-004",
                    api="/api/checkout",
                    module="checkout"
                )
            )
        ]

        summary = SecuritySummary(
            total_findings=1,
            critical=0,
            high=1,
            medium=0,
            low=0
        )

        metrics = SecurityMetrics(
            coverage=0.0,
            confidence=0.5
        )

        return SecurityReport(
            run_id=run_id,
            stage="security",
            version=version,
            summary=summary,
            findings=findings,
            dependency_vulnerabilities=[],
            llm_findings=[],
            metrics=metrics
        )

    def run(self, run_id: str = "RUN-0001", version: str = "v1") -> dict:
        """
        Runs the Security Agent skeleton.

        It creates:
        - SecurityReport_v1.json
        - SecurityReport_v1.md
        """

        report = self.create_dummy_report(run_id=run_id, version=version)

        output_dir = self.output_root / "runs" / run_id / "security" / version
        output_dir.mkdir(parents=True, exist_ok=True)

        json_path = output_dir / f"SecurityReport_{version}.json"
        md_path = output_dir / f"SecurityReport_{version}.md"

        json_path.write_text(
            json.dumps(report.model_dump(), indent=2),
            encoding="utf-8"
        )

        markdown_content = render_security_report_markdown(report)

        md_path.write_text(
            markdown_content,
            encoding="utf-8"
        )

        return {
            "run_id": run_id,
            "stage": "security",
            "version": version,
            "json_path": str(json_path),
            "markdown_path": str(md_path),
            "summary": report.summary.model_dump()
        }