import json
from pathlib import Path
from typing import List

from agents.tester_agent.schemas import (
    TestReport,
    TestSummary,
    TestCase,
    TestExecutionResult,
    TestMetrics,
    GeneratedTestFile,
    PytestRunResult
)
from agents.tester_agent.renderer import render_test_report_markdown
from agents.tester_agent.test_generator import PytestTestGenerator
from agents.tester_agent.runner import PytestRunner
from tools.artifact_registry import ArtifactRegistry


class TesterAgent:
    """
    Testing / QA Agent for AutoForge.

    Step 3:
    - Generates pytest files.
    - Executes generated pytest files.
    - Captures pytest output.
    - Updates TestReport JSON and Markdown with execution summary.
    """

    def __init__(self, output_root: str = "outputs"):
        self.output_root = Path(output_root)
        self.artifact_registry = ArtifactRegistry(output_root=output_root)
        self.test_generator = PytestTestGenerator()
        self.runner = PytestRunner()

    def run(
        self,
        run_id: str = "RUN-0001",
        version: str = "v1",
        target_path: str = "./sample_ecommerce_app"
    ) -> dict:
        """
        Run the Testing Agent and generate TestReport JSON + Markdown.
        """

        output_dir = self.output_root / "runs" / run_id / "tests" / version
        output_dir.mkdir(parents=True, exist_ok=True)

        generated_test_files = self.test_generator.generate_tests(
            target_path=target_path,
            output_dir=output_dir
        )

        generated_tests_path = output_dir / "generated_tests"

        pytest_result = self.runner.run_tests(str(generated_tests_path))

        execution_results = self.runner.build_execution_results(pytest_result)

        counts = self.runner.extract_counts(pytest_result)

        report = self.create_report(
            run_id=run_id,
            version=version,
            target_path=target_path,
            generated_tests_path=str(generated_tests_path),
            generated_test_files=generated_test_files,
            pytest_result=pytest_result,
            execution_results=execution_results,
            counts=counts
        )

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

        artifacts = [
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
            },
            {
                "stage": "testing",
                "version": version,
                "type": "generated_tests_folder",
                "format": "folder",
                "path": str(generated_tests_path),
                "description": "Folder containing generated pytest files."
            }
        ]

        for generated_file in generated_test_files:
            artifacts.append(
                {
                    "stage": "testing",
                    "version": version,
                    "type": "generated_test_file",
                    "format": "py",
                    "path": generated_file.file_path,
                    "description": generated_file.description
                }
            )

        metadata_path = self.artifact_registry.register_many(
            run_id=run_id,
            artifacts=artifacts
        )

        return {
            "run_id": run_id,
            "stage": "testing",
            "version": version,
            "target_path": target_path,
            "json_path": str(json_path),
            "markdown_path": str(md_path),
            "metadata_path": metadata_path,
            "generated_tests_path": str(generated_tests_path),
            "generated_test_files_count": len(generated_test_files),
            "pytest_status": pytest_result.status,
            "pytest_exit_code": pytest_result.exit_code,
            "summary": report.summary.model_dump(),
            "metrics": report.metrics.model_dump()
        }

    def create_report(
        self,
        run_id: str,
        version: str,
        target_path: str,
        generated_tests_path: str,
        generated_test_files: List[GeneratedTestFile],
        pytest_result: PytestRunResult,
        execution_results: List[TestExecutionResult],
        counts: dict
    ) -> TestReport:
        """
        Create test report after generating and executing pytest files.
        """

        test_cases: List[TestCase] = [
            TestCase(
                test_id="TC-001",
                title="Validate generated project structure",
                description="Checks whether the generated project folder exists and contains source files.",
                test_type="smoke",
                target_module="project",
                target_file=target_path,
                related_requirement_id="NFR-TEST-001",
                expected_result="Target project folder should exist and contain source files."
            ),
            TestCase(
                test_id="TC-002",
                title="Validate Python source syntax",
                description="Checks whether Python files in the generated project compile successfully.",
                test_type="unit",
                target_module="backend",
                target_file=target_path,
                related_requirement_id="NFR-TEST-002",
                expected_result="All Python files should compile without syntax errors."
            ),
            TestCase(
                test_id="TC-003",
                title="Validate minimum e-commerce feature representation",
                description="Checks whether catalog/product, cart, checkout/order concepts exist in generated code.",
                test_type="integration",
                target_module="ecommerce",
                target_file=target_path,
                related_requirement_id="FR-001",
                expected_result="Generated code should include catalog/product, cart, and checkout/order features."
            )
        ]

        summary = TestSummary(
            total_tests=counts["total"],
            passed=counts["passed"],
            failed=counts["failed"],
            skipped=counts["skipped"],
            not_run=counts["not_run"]
        )

        pass_rate = 0.0

        if summary.total_tests > 0:
            pass_rate = round(summary.passed / summary.total_tests, 2)

        metrics = TestMetrics(
            test_coverage=round(len(generated_test_files) / max(len(test_cases), 1), 2),
            pass_rate=pass_rate,
            execution_efficiency=pytest_result.duration_ms
        )

        recommendations = [
            "Generated pytest files were executed.",
            "Step 4 will improve detailed individual test parsing.",
            "Review failed tests before moving to Security Agent validation."
        ]

        if summary.failed > 0:
            recommendations.insert(
                0,
                "Some generated tests failed. Review pytest stdout/stderr in TestReport_v1.json."
            )

        return TestReport(
            run_id=run_id,
            stage="testing",
            version=version,
            target_path=target_path,
            generated_tests_path=generated_tests_path,
            generated_test_files=generated_test_files,
            pytest_run=pytest_result,
            summary=summary,
            test_cases=test_cases,
            execution_results=execution_results,
            metrics=metrics,
            recommendations=recommendations
        )