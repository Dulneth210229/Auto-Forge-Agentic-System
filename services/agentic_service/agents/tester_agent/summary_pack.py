from datetime import datetime, timezone
from typing import Dict, Any, List

from agents.tester_agent.schemas import TestReport


class TestSummaryPackBuilder:
    """
    Builds a compact dashboard/API-friendly summary from the full TestReport.

    The full TestReport is useful for detailed QA review.
    The summary pack is useful for:
    - dashboards
    - orchestrator decisions
    - approval gates
    - quick API responses
    """

    FAILED_TEST_LIMIT = 10

    def build(
        self,
        report: TestReport,
        json_report_path: str,
        markdown_report_path: str,
        target_path: str
    ) -> Dict[str, Any]:
        """
        Build summary pack as a plain dictionary.
        """

        failed_results = self._get_failed_results(report)

        return {
            "run_id": report.run_id,
            "stage": report.stage,
            "version": report.version,
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "target_path": target_path,
            "summary": report.summary.model_dump(),
            "metrics": report.metrics.model_dump(),
            "pytest_run": report.pytest_run.model_dump() if report.pytest_run else None,
            "traceability_summary": report.traceability_summary.model_dump(),
            "counts": {
                "generated_test_files": len(report.generated_test_files),
                "test_cases": len(report.test_cases),
                "execution_results": len(report.execution_results),
                "regression_test_cases": len(report.regression_test_cases),
                "security_validation_cases": len(report.security_validation_cases),
                "failed_results": len(failed_results)
            },
            "quality_gate": self._build_quality_gate(report),
            "failed_results": failed_results,
            "recommendations": report.recommendations,
            "artifacts": {
                "test_report_json": json_report_path,
                "test_report_markdown": markdown_report_path,
                "test_summary_pack_json": "",
                "test_summary_pack_markdown": "",
                "generated_tests_path": report.generated_tests_path,
                "regression_tests_path": report.regression_tests_path,
                "security_validation_tests_path": report.security_validation_tests_path
            }
        }

    def _build_quality_gate(self, report: TestReport) -> Dict[str, Any]:
        """
        Build testing quality gate decision.

        Simple MVP policy:
        - FAIL if any test failed or pytest process errored
        - WARN if tests were skipped
        - PASS if all tests passed
        """

        if report.pytest_run and report.pytest_run.status == "error":
            return {
                "status": "FAIL",
                "reason": "Pytest execution had a process-level error.",
                "policy": "FAIL if pytest status is error or failed tests exist."
            }

        if report.summary.failed > 0:
            return {
                "status": "FAIL",
                "reason": f"{report.summary.failed} test(s) failed.",
                "policy": "FAIL if any generated test fails."
            }

        if report.summary.skipped > 0:
            return {
                "status": "WARN",
                "reason": f"{report.summary.skipped} test(s) were skipped.",
                "policy": "WARN if tests are skipped but no tests fail."
            }

        return {
            "status": "PASS",
            "reason": "All generated tests passed.",
            "policy": "PASS when pytest succeeds and no tests fail or skip."
        }

    def _get_failed_results(self, report: TestReport) -> List[Dict[str, Any]]:
        """
        Return failed execution results for dashboard display.
        """

        failed = [
            result for result in report.execution_results
            if result.status == "failed"
        ]

        failed = failed[: self.FAILED_TEST_LIMIT]

        return [
            {
                "test_id": result.test_id,
                "status": result.status,
                "message": result.message,
                "duration_ms": result.duration_ms
            }
            for result in failed
        ]


class TestSummaryPackRenderer:
    """
    Renders the testing summary pack dictionary into Markdown.
    """

    def render_markdown(self, pack: Dict[str, Any]) -> str:
        lines = [
            "# Test Summary Pack",
            "",
            f"**Run ID:** {pack['run_id']}  ",
            f"**Stage:** {pack['stage']}  ",
            f"**Version:** {pack['version']}  ",
            f"**Generated At:** {pack['generated_at']}  ",
            f"**Target Path:** {pack['target_path']}",
            "",
            "---",
            "",
            "## 1. Quality Gate",
            "",
            "| Field | Value |",
            "|---|---|",
            f"| Status | **{pack['quality_gate']['status']}** |",
            f"| Reason | {pack['quality_gate']['reason']} |",
            f"| Policy | {pack['quality_gate']['policy']} |",
            "",
            "---",
            "",
            "## 2. Test Summary",
            "",
            "| Metric | Count |",
            "|---|---:|",
            f"| Total Tests | {pack['summary']['total_tests']} |",
            f"| Passed | {pack['summary']['passed']} |",
            f"| Failed | {pack['summary']['failed']} |",
            f"| Skipped | {pack['summary']['skipped']} |",
            f"| Not Run | {pack['summary']['not_run']} |",
            "",
            "---",
            "",
            "## 3. Metrics",
            "",
            "| Metric | Value |",
            "|---|---:|",
            f"| Test Coverage | {pack['metrics']['test_coverage']} |",
            f"| Pass Rate | {pack['metrics']['pass_rate']} |",
            f"| Execution Efficiency | {pack['metrics']['execution_efficiency']} ms |",
            "",
            "---",
            "",
            "## 4. Traceability Summary",
            "",
            "| Metric | Value |",
            "|---|---:|",
            f"| Total Test Cases | {pack['traceability_summary']['total_test_cases']} |",
            f"| Mapped Test Cases | {pack['traceability_summary']['mapped_test_cases']} |",
            f"| Partially Mapped Test Cases | {pack['traceability_summary']['partially_mapped_test_cases']} |",
            f"| Unmapped Test Cases | {pack['traceability_summary']['unmapped_test_cases']} |",
            f"| Coverage Percentage | {pack['traceability_summary']['coverage_percentage']}% |",
            "",
            "---",
            "",
            "## 5. Dashboard Counts",
            "",
            "| Item | Count |",
            "|---|---:|",
            f"| Generated Test Files | {pack['counts']['generated_test_files']} |",
            f"| Test Cases | {pack['counts']['test_cases']} |",
            f"| Execution Results | {pack['counts']['execution_results']} |",
            f"| Regression Test Cases | {pack['counts']['regression_test_cases']} |",
            f"| Security Validation Cases | {pack['counts']['security_validation_cases']} |",
            f"| Failed Results | {pack['counts']['failed_results']} |",
            "",
            "---",
            "",
            "## 6. Failed Results",
            ""
        ]

        failed_results = pack.get("failed_results", [])

        if failed_results:
            lines.extend([
                "| Test ID | Status | Duration | Message |",
                "|---|---|---:|---|"
            ])

            for result in failed_results:
                lines.append(
                    f"| {result['test_id']} | {result['status']} | "
                    f"{result['duration_ms']} ms | {result['message']} |"
                )
        else:
            lines.append("No failed test results.")

        lines.extend([
            "",
            "---",
            "",
            "## 7. Recommendations",
            ""
        ])

        recommendations = pack.get("recommendations", [])

        if recommendations:
            for recommendation in recommendations:
                lines.append(f"- {recommendation}")
        else:
            lines.append("No recommendations.")

        lines.extend([
            "",
            "---",
            "",
            "## 8. Artifact Paths",
            "",
            "| Artifact | Path |",
            "|---|---|",
            f"| Test Report JSON | {pack['artifacts']['test_report_json']} |",
            f"| Test Report Markdown | {pack['artifacts']['test_report_markdown']} |",
            f"| Test Summary Pack JSON | {pack['artifacts']['test_summary_pack_json']} |",
            f"| Test Summary Pack Markdown | {pack['artifacts']['test_summary_pack_markdown']} |",
            f"| Generated Tests Folder | {pack['artifacts']['generated_tests_path']} |",
            f"| Regression Tests Folder | {pack['artifacts']['regression_tests_path']} |",
            f"| Security Validation Tests Folder | {pack['artifacts']['security_validation_tests_path']} |",
            ""
        ])

        return "\n".join(lines)