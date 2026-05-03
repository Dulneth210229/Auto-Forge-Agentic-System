from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Any, List

from agents.security_agent.schemas import SecurityReport


class SecuritySummaryPackBuilder:
    """
    Builds a compact dashboard/API-friendly summary from the full SecurityReport.

    The full report is useful for audit and detailed review.
    The summary pack is useful for:
    - dashboards
    - API response previews
    - orchestrator decisions
    - human approval screens
    """

    TOP_FINDINGS_LIMIT = 10

    def build(
        self,
        report: SecurityReport,
        json_report_path: str,
        markdown_report_path: str,
        deduplication_summary: Dict[str, Any],
        target_path: str | None
    ) -> Dict[str, Any]:
        """
        Build summary pack as plain dictionary so it is easy to save as JSON.
        """

        traceability_coverage = self._calculate_traceability_coverage(report)
        top_blocking_findings = self._get_top_blocking_findings(report)

        return {
            "run_id": report.run_id,
            "stage": report.stage,
            "version": report.version,
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "target_path": target_path,
            "security_gate": report.security_gate.model_dump(),
            "summary": report.summary.model_dump(),
            "metrics": report.metrics.model_dump(),
            "deduplication": deduplication_summary,
            "counts": {
                "total_findings": report.summary.total_findings,
                "dependency_vulnerabilities": len(report.dependency_vulnerabilities),
                "llm_findings": len(report.llm_findings),
                "fix_suggestions": len(report.fix_suggestions),
                "top_blocking_findings": len(top_blocking_findings)
            },
            "traceability": {
                "coverage_percentage": traceability_coverage,
                "mapped_findings": self._count_mapped_findings(report),
                "total_findings": report.summary.total_findings
            },
            "top_blocking_findings": top_blocking_findings,
            "artifacts": {
                "security_report_json": json_report_path,
                "security_report_markdown": markdown_report_path,
                "security_summary_pack_json": "",
                "security_summary_pack_markdown": ""
            }
        }

    def _calculate_traceability_coverage(self, report: SecurityReport) -> float:
        """
        Calculate percentage of findings that have requirement/module/API mapping.
        """

        total = report.summary.total_findings

        if total == 0:
            return 0.0

        mapped = self._count_mapped_findings(report)

        return round((mapped / total) * 100, 2)

    def _count_mapped_findings(self, report: SecurityReport) -> int:
        """
        Count findings with non-empty traceability fields.
        """

        mapped = 0

        for finding in report.findings:
            traceability = finding.traceability

            if (
                traceability.requirement_id
                and traceability.api
                and traceability.module
            ):
                mapped += 1

        return mapped

    def _get_top_blocking_findings(self, report: SecurityReport) -> List[Dict[str, Any]]:
        """
        Return the most important findings for dashboard display.

        Priority:
        1. Critical findings
        2. High findings
        3. Findings listed in security_gate.blocking_findings
        """

        blocking_ids = set(report.security_gate.blocking_findings)

        priority_findings = [
            finding for finding in report.findings
            if finding.severity in ["Critical", "High"]
            or finding.finding_id in blocking_ids
        ]

        priority_findings = priority_findings[: self.TOP_FINDINGS_LIMIT]

        return [
            {
                "finding_id": finding.finding_id,
                "title": finding.title,
                "severity": finding.severity,
                "file": finding.file,
                "line": finding.line,
                "detection_method": finding.detection_method,
                "cwe": finding.cwe,
                "requirement_id": finding.traceability.requirement_id,
                "api": finding.traceability.api,
                "module": finding.traceability.module,
                "recommendation": finding.recommendation
            }
            for finding in priority_findings
        ]


class SecuritySummaryPackRenderer:
    """
    Renders the summary pack dictionary into Markdown.
    """

    def render_markdown(self, pack: Dict[str, Any]) -> str:
        top_findings = pack.get("top_blocking_findings", [])

        lines = [
            "# Security Summary Pack",
            "",
            f"**Run ID:** {pack['run_id']}  ",
            f"**Stage:** {pack['stage']}  ",
            f"**Version:** {pack['version']}  ",
            f"**Generated At:** {pack['generated_at']}  ",
            f"**Target Path:** {pack.get('target_path') or 'N/A'}",
            "",
            "---",
            "",
            "## 1. Security Gate",
            "",
            "| Field | Value |",
            "|---|---|",
            f"| Status | **{pack['security_gate']['status']}** |",
            f"| Reason | {pack['security_gate']['reason']} |",
            f"| Policy | {pack['security_gate']['policy']} |",
            "",
            "---",
            "",
            "## 2. Severity Summary",
            "",
            "| Severity | Count |",
            "|---|---:|",
            f"| Critical | {pack['summary']['critical']} |",
            f"| High | {pack['summary']['high']} |",
            f"| Medium | {pack['summary']['medium']} |",
            f"| Low | {pack['summary']['low']} |",
            f"| **Total** | **{pack['summary']['total_findings']}** |",
            "",
            "---",
            "",
            "## 3. Dashboard Counts",
            "",
            "| Metric | Count |",
            "|---|---:|",
            f"| Dependency Vulnerabilities | {pack['counts']['dependency_vulnerabilities']} |",
            f"| LLM Findings | {pack['counts']['llm_findings']} |",
            f"| Fix Suggestions | {pack['counts']['fix_suggestions']} |",
            f"| Top Blocking Findings | {pack['counts']['top_blocking_findings']} |",
            "",
            "---",
            "",
            "## 4. Traceability",
            "",
            "| Metric | Value |",
            "|---|---:|",
            f"| Coverage Percentage | {pack['traceability']['coverage_percentage']}% |",
            f"| Mapped Findings | {pack['traceability']['mapped_findings']} |",
            f"| Total Findings | {pack['traceability']['total_findings']} |",
            "",
            "---",
            "",
            "## 5. Deduplication",
            "",
            "| Metric | Value |",
            "|---|---:|",
            f"| Before Deduplication | {pack['deduplication']['findings_before_deduplication']} |",
            f"| After Deduplication | {pack['deduplication']['findings_after_deduplication']} |",
            f"| Duplicates Removed | {pack['deduplication']['duplicates_removed']} |",
            "",
            "---",
            "",
            "## 6. Top Blocking Findings",
            ""
        ]

        if top_findings:
            lines.extend([
                "| ID | Title | Severity | File | Method | Requirement | Module |",
                "|---|---|---|---|---|---|---|"
            ])

            for finding in top_findings:
                lines.append(
                    f"| {finding['finding_id']} | {finding['title']} | "
                    f"{finding['severity']} | {finding['file']} | "
                    f"{finding['detection_method']} | {finding['requirement_id']} | "
                    f"{finding['module']} |"
                )
        else:
            lines.append("No blocking findings.")

        lines.extend([
            "",
            "---",
            "",
            "## 7. Artifact Paths",
            "",
            "| Artifact | Path |",
            "|---|---|",
            f"| Security Report JSON | {pack['artifacts']['security_report_json']} |",
            f"| Security Report Markdown | {pack['artifacts']['security_report_markdown']} |",
            f"| Summary Pack JSON | {pack['artifacts']['security_summary_pack_json']} |",
            f"| Summary Pack Markdown | {pack['artifacts']['security_summary_pack_markdown']} |",
            ""
        ])

        return "\n".join(lines)