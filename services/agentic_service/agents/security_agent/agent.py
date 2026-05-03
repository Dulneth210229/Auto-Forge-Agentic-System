import json
from pathlib import Path
from typing import List, Dict, Any

from agents.security_agent.schemas import (
    SecurityReport,
    SecuritySummary,
    SecurityFinding,
    SecurityMetrics,
    SecurityGateDecision,
    SecurityFixSuggestion
)
from agents.security_agent.renderer import render_security_report_markdown
from agents.security_agent.scanners.multi_scanner import MultiSecurityScanner
from agents.security_agent.llm_reviewer import LLMSecureCodeReviewer
from agents.security_agent.deduplicator import FindingDeduplicator
from agents.security_agent.gate import SecurityGateEvaluator
from agents.security_agent.traceability import SecurityTraceabilityMapper
from agents.security_agent.fix_suggester import SecurityFixSuggester
from agents.security_agent.summary_pack import (
    SecuritySummaryPackBuilder,
    SecuritySummaryPackRenderer
)
from tools.llm.provider import OllamaProvider
from tools.artifact_registry import ArtifactRegistry


class SecurityAgent:
    """
    Security Agent for AutoForge.

    Current capabilities:
    - Python AST scanning
    - JavaScript/TypeScript pattern scanning
    - Secret scanning
    - Config scanning
    - Dependency scanning with OSV.dev
    - Ollama LLM-assisted secure code review
    - Finding deduplication
    - Traceability mapping
    - Security gate decision
    - Structured fix suggestions
    - Security summary pack generation
    - Run metadata artifact registration
    """

    def __init__(self, output_root: str = "outputs"):
        """
        Initialize Security Agent dependencies.

        Args:
            output_root: Root output folder. Default is "outputs".
        """

        self.output_root = Path(output_root)

        # Runs all rule-based scanners:
        # Python AST, JS/TS, Secret, Config, Dependency.
        self.scanner = MultiSecurityScanner()

        # Removes duplicate findings between rule-based scanners and LLM review.
        self.deduplicator = FindingDeduplicator()

        # Maps findings to requirement ID, API, and module.
        self.traceability_mapper = SecurityTraceabilityMapper()

        # Evaluates PASS / WARN / FAIL security gate.
        self.gate_evaluator = SecurityGateEvaluator()

        # Generates structured remediation guidance for each finding.
        self.fix_suggester = SecurityFixSuggester()

        # Builds compact dashboard/API-friendly summary artifacts.
        self.summary_pack_builder = SecuritySummaryPackBuilder()
        self.summary_pack_renderer = SecuritySummaryPackRenderer()

        # Registers generated artifacts into outputs/runs/{run_id}/run_metadata.json.
        self.artifact_registry = ArtifactRegistry(output_root=output_root)

    def run(
        self,
        run_id: str = "RUN-0001",
        version: str = "v1",
        target_path: str | None = None,
        enable_llm: bool = False
    ) -> dict:
        """
        Run the Security Agent.

        Args:
            run_id: Current AutoForge run ID.
            version: Artifact version, for example "v1".
            target_path: Source code folder to scan.
            enable_llm: If True, run Ollama LLM-assisted secure code review.

        Returns:
            Dictionary containing output paths and summary data.
        """

        llm_findings_data: List[Dict[str, Any]] = []

        # ---------------------------------------------------------
        # 1. Run scanners
        # ---------------------------------------------------------
        if target_path:
            findings = self.scanner.scan_directory(target_path)
            dependency_vulnerabilities = self.scanner.get_dependency_vulnerabilities()

            # Optional LLM-assisted review.
            if enable_llm:
                llm_reviewer = LLMSecureCodeReviewer(
                    llm_provider=OllamaProvider(),
                    factory=self.scanner.get_factory()
                )

                llm_security_findings = llm_reviewer.review_directory(target_path)

                findings.extend(llm_security_findings)
                llm_findings_data = llm_reviewer.llm_findings
        else:
            findings = []
            dependency_vulnerabilities = []

        # ---------------------------------------------------------
        # 2. Deduplicate findings
        # ---------------------------------------------------------
        before_dedup_count = len(findings)

        findings = self.deduplicator.deduplicate(findings)

        after_dedup_count = len(findings)

        deduplication_summary = self.deduplicator.summarize_deduplication(
            before_count=before_dedup_count,
            after_count=after_dedup_count
        )

        # ---------------------------------------------------------
        # 3. Add traceability mapping
        # ---------------------------------------------------------
        findings = self.traceability_mapper.map_findings(findings)

        # ---------------------------------------------------------
        # 4. Evaluate security gate
        # ---------------------------------------------------------
        security_gate = self.gate_evaluator.evaluate(findings)

        # ---------------------------------------------------------
        # 5. Generate fix suggestions
        # ---------------------------------------------------------
        fix_suggestions = self.fix_suggester.generate_fix_suggestions(findings)

        # ---------------------------------------------------------
        # 6. Create full Security Report object
        # ---------------------------------------------------------
        report = self.create_report(
            run_id=run_id,
            version=version,
            findings=findings,
            dependency_vulnerabilities=dependency_vulnerabilities,
            llm_findings=llm_findings_data,
            security_gate=security_gate,
            fix_suggestions=fix_suggestions
        )

        # ---------------------------------------------------------
        # 7. Save full JSON + Markdown report
        # ---------------------------------------------------------
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

        # ---------------------------------------------------------
        # 8. Build and save compact Security Summary Pack
        # ---------------------------------------------------------
        summary_pack_json_path = output_dir / f"SecuritySummaryPack_{version}.json"
        summary_pack_md_path = output_dir / f"SecuritySummaryPack_{version}.md"

        summary_pack = self.summary_pack_builder.build(
            report=report,
            json_report_path=str(json_path),
            markdown_report_path=str(md_path),
            deduplication_summary=deduplication_summary,
            target_path=target_path
        )

        summary_pack["artifacts"]["security_summary_pack_json"] = str(summary_pack_json_path)
        summary_pack["artifacts"]["security_summary_pack_markdown"] = str(summary_pack_md_path)

        summary_pack_json_path.write_text(
            json.dumps(summary_pack, indent=2),
            encoding="utf-8"
        )

        summary_pack_md_path.write_text(
            self.summary_pack_renderer.render_markdown(summary_pack),
            encoding="utf-8"
        )

        # ---------------------------------------------------------
        # 9. Register generated artifacts in run_metadata.json
        # ---------------------------------------------------------
        metadata_path = self.artifact_registry.register_many(
            run_id=run_id,
            artifacts=[
                {
                    "stage": "security",
                    "version": version,
                    "type": "security_report_json",
                    "format": "json",
                    "path": str(json_path),
                    "description": "Full machine-readable Security Report."
                },
                {
                    "stage": "security",
                    "version": version,
                    "type": "security_report_markdown",
                    "format": "md",
                    "path": str(md_path),
                    "description": "Human-readable Security Report."
                },
                {
                    "stage": "security",
                    "version": version,
                    "type": "security_summary_pack_json",
                    "format": "json",
                    "path": str(summary_pack_json_path),
                    "description": "Compact dashboard/API Security Summary Pack."
                },
                {
                    "stage": "security",
                    "version": version,
                    "type": "security_summary_pack_markdown",
                    "format": "md",
                    "path": str(summary_pack_md_path),
                    "description": "Human-readable Security Summary Pack."
                }
            ]
        )

        # ---------------------------------------------------------
        # 10. Return CLI/API response
        # ---------------------------------------------------------
        return {
            "run_id": run_id,
            "stage": "security",
            "version": version,
            "target_path": target_path,
            "llm_enabled": enable_llm,
            "json_path": str(json_path),
            "markdown_path": str(md_path),
            "summary_pack_json_path": str(summary_pack_json_path),
            "summary_pack_markdown_path": str(summary_pack_md_path),
            "metadata_path": metadata_path,
            "summary": report.summary.model_dump(),
            "dependency_vulnerabilities_count": len(dependency_vulnerabilities),
            "llm_findings_count": len(llm_findings_data),
            "deduplication": deduplication_summary,
            "security_gate": report.security_gate.model_dump(),
            "traceability_mapped": True,
            "fix_suggestions_count": len(fix_suggestions)
        }

    def create_report(
        self,
        run_id: str,
        version: str,
        findings: List[SecurityFinding],
        dependency_vulnerabilities: List[Dict[str, Any]],
        llm_findings: List[Dict[str, Any]],
        security_gate: SecurityGateDecision,
        fix_suggestions: List[SecurityFixSuggestion]
    ) -> SecurityReport:
        """
        Create the final SecurityReport object.

        Args:
            run_id: Current AutoForge run ID.
            version: Artifact version.
            findings: Final deduplicated security findings.
            dependency_vulnerabilities: Normalized dependency vulnerability records.
            llm_findings: Raw LLM finding records for audit.
            security_gate: PASS/WARN/FAIL decision.
            fix_suggestions: Structured remediation suggestions.

        Returns:
            SecurityReport Pydantic object.
        """

        summary = self._build_summary(findings)

        metrics = SecurityMetrics(
            coverage=1.0 if findings else 0.0,
            confidence=0.85 if llm_findings else 0.8 if findings else 0.0
        )

        return SecurityReport(
            run_id=run_id,
            stage="security",
            version=version,
            summary=summary,
            findings=findings,
            dependency_vulnerabilities=dependency_vulnerabilities,
            llm_findings=llm_findings,
            security_gate=security_gate,
            fix_suggestions=fix_suggestions,
            metrics=metrics
        )

    def _build_summary(self, findings: List[SecurityFinding]) -> SecuritySummary:
        """
        Count security findings by severity.

        Args:
            findings: List of final deduplicated security findings.

        Returns:
            SecuritySummary object.
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