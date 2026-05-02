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
from tools.llm.provider import OllamaProvider


class SecurityAgent:
    """
    Security Agent.

    Current capabilities:
    - Python AST scanning
    - JavaScript/TypeScript pattern scanning
    - Secret scanning
    - Config scanning
    - Dependency scanning with OSV.dev
    - Ollama LLM-assisted secure code review
    - Finding deduplication
    - Security gate decision
    - Traceability mapping
    - Structured fix suggestions
    """

    def __init__(self, output_root: str = "outputs"):
        self.output_root = Path(output_root)
        self.scanner = MultiSecurityScanner()
        self.deduplicator = FindingDeduplicator()
        self.gate_evaluator = SecurityGateEvaluator()
        self.traceability_mapper = SecurityTraceabilityMapper()
        self.fix_suggester = SecurityFixSuggester()

    def run(
        self,
        run_id: str = "RUN-0001",
        version: str = "v1",
        target_path: str | None = None,
        enable_llm: bool = False
    ) -> dict:
        """
        Runs the Security Agent.
        """

        llm_findings_data: List[Dict[str, Any]] = []

        if target_path:
            findings = self.scanner.scan_directory(target_path)
            dependency_vulnerabilities = self.scanner.get_dependency_vulnerabilities()

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

        before_dedup_count = len(findings)

        findings = self.deduplicator.deduplicate(findings)

        after_dedup_count = len(findings)

        deduplication_summary = self.deduplicator.summarize_deduplication(
            before_count=before_dedup_count,
            after_count=after_dedup_count
        )

        findings = self.traceability_mapper.map_findings(findings)

        security_gate = self.gate_evaluator.evaluate(findings)

        fix_suggestions = self.fix_suggester.generate_fix_suggestions(findings)

        report = self.create_report(
            run_id=run_id,
            version=version,
            findings=findings,
            dependency_vulnerabilities=dependency_vulnerabilities,
            llm_findings=llm_findings_data,
            security_gate=security_gate,
            fix_suggestions=fix_suggestions
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
            "llm_enabled": enable_llm,
            "json_path": str(json_path),
            "markdown_path": str(md_path),
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
        Creates the final SecurityReport object from all scanner findings.
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