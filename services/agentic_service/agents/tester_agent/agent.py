import json
from pathlib import Path
from typing import List

from agents.tester_agent.schemas import (
    TestReport,
    TestSummary,
    TestCase,
    TestExecutionResult,
    TestMetrics
)
from agents.tester_agent.renderer import render_test_report_markdown
from tools.artifact_registry import ArtifactRegistry


class TesterAgent:
    """
    Testing / QA Agent for AutoForge.

    Step 1:
    - Creates a skeleton QA report.
    - Saves JSON and Markdown outputs.
    - Registers test artifacts in run_metadata.json.

    Later steps will add:
    - pytest test generation
    - pytest execution
    - result parsing
    - coverage metrics
    - security finding validation
    """

    def __init__(self, output_root: str = "outputs"):
        self.output_root = Path(output_root)
        self.artifact_registry = ArtifactRegistry(output_root=output_root)

    def run(
        self,
        run_id: str = "RUN-0001",
        version: str = "v1",
        target_path: str = "./sample_ecommerce_app"
    ) -> dict:
        """
        Run the Testing Agent and generate TestReport JSON + Markdown.
        """

        report = self.create_dummy_report(
            run_id=run_id,
            version=version,
            target_path=target_path
        )

        output_dir = self.output_root / "runs" / run_id / "tests" / version
        output_dir.mkdir(parents=True, exist_ok=True)

        json_path = output_dir / f"TestReport_{version}.json"
        md_path = output_dir / f"TestReport_{version}.md"

        json_path.write_text(
            json.dumps(report.model_dump(), indent=2),
            encoding="utf-8"
        )

        markdown_content = render_test_report_markdown(report)

        md_path.write_text(
            markdown_content,
            encoding="utf-8"
        )

        metadata_path = self.artifact_registry.register_many(
            run_id=run_id,
            artifacts=[
                {
                    "stage": "testing",
                    "version": version,
                    "type": "test_report_json",
                    "format": "json",
                    "path": str(json_path),
                    "description": "Machine-readable Testing Agent report."
                },
                {
                    "stage": "testing",
                    "version": version,
                    "type": "test_report_markdown",
                    "format": "md",
                    "path": str(md_path),
                    "description": "Human-readable Testing Agent report."
                }
            ]
        )

        return {
            "run_id": run_id,
            "stage": "testing",
            "version": version,
            "target_path": target_path,
            "json_path": str(json_path),
            "markdown_path": str(md_path),
            "metadata_path": metadata_path,
            "summary": report.summary.model_dump(),
            "metrics": report.metrics.model_dump()
        }

    def create_dummy_report(
        self,
        run_id: str,
        version: str,
        target_path: str
    ) -> TestReport:
        """
        Create a dummy test report for the skeleton stage.
        """

        test_cases: List[TestCase] = [
            TestCase(
                test_id="TC-001",
                title="Validate product catalog workflow",
                description="Check whether product catalog behavior can be tested.",
                test_type="api",
                target_module="catalog",
                target_file=f"{target_path}/app.py",
                related_requirement_id="FR-001",
                expected_result="Catalog should return valid product data."
            ),
            TestCase(
                test_id="TC-002",
                title="Validate cart operation workflow",
                description="Check whether cart add/remove behavior can be tested.",
                test_type="integration",
                target_module="cart",
                target_file=f"{target_path}/app.py",
                related_requirement_id="FR-002",
                expected_result="Cart should update correctly when items are added or removed."
            ),
            TestCase(
                test_id="TC-003",
                title="Validate checkout workflow",
                description="Check whether checkout input handling can be tested.",
                test_type="api",
                target_module="checkout",
                target_file=f"{target_path}/app.py",
                related_requirement_id="FR-003",
                expected_result="Checkout should accept valid data and reject invalid data."
            )
        ]

        execution_results: List[TestExecutionResult] = [
            TestExecutionResult(
                test_id="TC-001",
                status="not_run",
                message="Skeleton stage only. Test execution will be added in the next step.",
                duration_ms=0
            ),
            TestExecutionResult(
                test_id="TC-002",
                status="not_run",
                message="Skeleton stage only. Test execution will be added in the next step.",
                duration_ms=0
            ),
            TestExecutionResult(
                test_id="TC-003",
                status="not_run",
                message="Skeleton stage only. Test execution will be added in the next step.",
                duration_ms=0
            )
        ]

        summary = TestSummary(
            total_tests=len(test_cases),
            passed=0,
            failed=0,
            skipped=0,
            not_run=len(test_cases)
        )

        metrics = TestMetrics(
            test_coverage=0.0,
            pass_rate=0.0,
            execution_efficiency=0.0
        )

        return TestReport(
            run_id=run_id,
            stage="testing",
            version=version,
            target_path=target_path,
            summary=summary,
            test_cases=test_cases,
            execution_results=execution_results,
            metrics=metrics,
            recommendations=[
                "Add pytest test generation in the next step.",
                "Connect generated tests to functional requirements.",
                "Later use Testing Agent results to validate fixes after Coder Agent changes."
            ]
        )