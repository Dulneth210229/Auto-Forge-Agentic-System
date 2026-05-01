import json
from pathlib import Path
from typing import List

from agents.security_agent.schemas import (
    SecurityReport,
    SecuritySummary,
    SecurityFinding,
    SecurityMetrics
)
from agents.security_agent.renderer import render_security_report_markdown
from agents.security_agent.scanners.multi_scanner import MultiSecurityScanner


class SecurityAgent:
    """
    Security Agent.

    Step 1:
    - Generated dummy security reports.

    Step 2:
    - Added Python AST scanning.

    Step 4:
    - Extended to multi-scanner architecture:
      - Python AST Scanner
      - JavaScript/TypeScript Scanner
      - Secret Scanner
      - Config Scanner
    """

    def __init__(self, output_root: str = "outputs"):
        self.output_root = Path(output_root)
        self.scanner = MultiSecurityScanner()

    def run(
        self,
        run_id: str = "RUN-0001",
        version: str = "v1",
        target_path: str | None = None
    ) -> dict:
        """
        Runs the Security Agent.

        If target_path is provided:
            - Scan real project source code.

        If target_path is not provided:
            - Generate an empty report.
        """

        if target_path:
            findings = self.scanner.scan_directory(target_path)
        else:
            findings = []

        report = self.create_report(
            run_id=run_id,
            version=version,
            findings=findings
        )

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
            "target_path": target_path,
            "json_path": str(json_path),
            "markdown_path": str(md_path),
            "summary": report.summary.model_dump()
        }

    def create_report(
        self,
        run_id: str,
        version: str,
        findings: List[SecurityFinding]
    ) -> SecurityReport:
        """
        Creates the final SecurityReport object from scanner findings.
        """

        summary = self._build_summary(findings)

        metrics = SecurityMetrics(
            coverage=1.0 if findings else 0.0,
            confidence=0.8 if findings else 0.0
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

    def _build_summary(self, findings: List[SecurityFinding]) -> SecuritySummary:
        """
        Count findings by severity.
        """

        critical = sum(1 for finding in findings if finding.severity == "Critical")
        high = sum(1 for finding in findings if finding.severity == "High")
        medium = sum(1 for finding in findings if finding.severity == "Medium")
        low = sum(1 for finding in findings if finding.severity == "Low")

        return SecuritySummary(
            total_findings=len(findings),
            critical=critical,
            high=high,
            medium=medium,
            low=low
        )