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
    PytestRunResult,
    RegressionTestCase,
    SecurityValidationCase,
    TestTraceabilitySummary
)
from agents.tester_agent.renderer import render_test_report_markdown
from agents.tester_agent.test_generator import PytestTestGenerator
from agents.tester_agent.runner import PytestRunner
from agents.tester_agent.traceability import TestTraceabilityMapper
from tools.artifact_registry import ArtifactRegistry


class TesterAgent:
    """
    Testing / QA Agent for AutoForge.

    Step 10:
    - Generates pytest files.
    - Executes generated pytest files.
    - Captures individual pytest test results.
    - Adds regression tests.
    - Adds security validation tests.
    - Adds traceability mapping for test cases.
    """

    def __init__(self, output_root: str = "outputs"):
        self.output_root = Path(output_root)
        self.artifact_registry = ArtifactRegistry(output_root=output_root)
        self.test_generator = PytestTestGenerator()
        self.runner = PytestRunner()
        self.traceability_mapper = TestTraceabilityMapper()

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
        regression_tests_path = output_dir / "regression_tests"
        security_validation_tests_path = output_dir / "security_validation_tests"

        collected_test_ids = self.runner.collect_test_ids(
            generated_tests_path=str(generated_tests_path)
        )

        pytest_result = self.runner.run_tests(
            generated_tests_path=str(generated_tests_path)
        )

        execution_results = self.runner.build_execution_results(
            pytest_result=pytest_result,
            collected_test_ids=collected_test_ids
        )

        counts = self.runner.extract_counts(
            pytest_result=pytest_result,
            execution_results=execution_results
        )

        regression_test_cases = self.test_generator.get_default_regression_cases()
        security_validation_cases = self.test_generator.get_default_security_validation_cases()

        report = self.create_report(
            run_id=run_id,
            version=version,
            target_path=target_path,
            generated_tests_path=str(generated_tests_path),
            generated_test_files=generated_test_files,
            regression_tests_path=str(regression_tests_path),
            regression_test_cases=regression_test_cases,
            security_validation_tests_path=str(security_validation_tests_path),
            security_validation_cases=security_validation_cases,
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
            },
            {
                "stage": "testing",
                "version": version,
                "type": "regression_tests_folder",
                "format": "folder",
                "path": str(regression_tests_path),
                "description": "Folder containing regression test metadata."
            },
            {
                "stage": "testing",
                "version": version,
                "type": "security_validation_tests_folder",
                "format": "folder",
                "path": str(security_validation_tests_path),
                "description": "Folder containing security validation test metadata."
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

        artifacts.append(
            {
                "stage": "testing",
                "version": version,
                "type": "regression_cases_json",
                "format": "json",
                "path": str(regression_tests_path / "regression_cases.json"),
                "description": "Machine-readable regression test scenarios."
            }
        )

        artifacts.append(
            {
                "stage": "testing",
                "version": version,
                "type": "security_validation_cases_json",
                "format": "json",
                "path": str(security_validation_tests_path / "security_validation_cases.json"),
                "description": "Machine-readable security validation test scenarios."
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
            "metrics": report.metrics.model_dump(),
            "traceability_summary": report.traceability_summary.model_dump()
        }

    def create_report(
        self,
        run_id: str,
        version: str,
        target_path: str,
        generated_tests_path: str,
        generated_test_files: List[GeneratedTestFile],
        regression_tests_path: str,
        regression_test_cases: List[RegressionTestCase],
        security_validation_tests_path: str,
        security_validation_cases: List[SecurityValidationCase],
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
                expected_result="Target project folder should exist and contain source files."
            ),
            TestCase(
                test_id="TC-002",
                title="Validate Python source syntax",
                description="Checks whether Python files in the generated project compile successfully.",
                test_type="unit",
                target_module="backend",
                target_file=target_path,
                expected_result="All Python files should compile without syntax errors."
            ),
            TestCase(
                test_id="TC-003",
                title="Validate minimum e-commerce feature representation",
                description="Checks whether catalog/product, cart, checkout/order concepts exist in generated code.",
                test_type="integration",
                target_module="ecommerce",
                target_file=target_path,
                expected_result="Generated code should include catalog/product, cart, and checkout/order features."
            ),
            TestCase(
                test_id="TC-004",
                title="Validate e-commerce API/function contracts",
                description="Checks whether generated code includes API or function contracts for catalog, cart, checkout, and order.",
                test_type="api",
                target_module="ecommerce_api",
                target_file=target_path,
                expected_result="Generated code should include API/function contracts for catalog, cart, checkout, and order."
            ),
            TestCase(
                test_id="TC-005",
                title="Validate full e-commerce integration workflow",
                description="Checks whether generated code supports product browsing, cart, checkout, and order workflow concepts.",
                test_type="integration",
                target_module="ecommerce_workflow",
                target_file=target_path,
                expected_result="Generated code should support Product -> Cart -> Checkout -> Order workflow."
            ),
            TestCase(
                test_id="TC-006",
                title="Validate e-commerce edge cases and input validation",
                description="Checks whether generated code includes common validation rules and edge-case handling.",
                test_type="integration",
                target_module="validation",
                target_file=target_path,
                expected_result="Generated code should include validation for invalid product IDs, quantities, empty carts, payment/customer data, prices, and stock."
            ),
            TestCase(
                test_id="TC-007",
                title="Validate regression cases",
                description="Checks whether known e-commerce bug patterns are prevented.",
                test_type="regression",
                target_module="regression",
                target_file=target_path,
                expected_result="Generated code should prevent known bugs from returning."
            ),
            TestCase(
                test_id="TC-008",
                title="Validate Security Agent report consistency",
                description="Checks whether SecurityReport_v1.json contains valid security gate, findings, fix suggestions, and traceability.",
                test_type="security_validation",
                target_module="security_validation",
                target_file="SecurityReport_v1.json",
                expected_result="Security report should be structurally valid and useful for downstream fixing."
            )
        ]

        test_cases = self.traceability_mapper.map_test_cases(test_cases)
        traceability_summary: TestTraceabilitySummary = (
            self.traceability_mapper.summarize_traceability(test_cases)
        )

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
            "Functional API-style tests were generated for catalog, cart, checkout, and order.",
            "Integration workflow tests were generated for Product -> Cart -> Checkout -> Order.",
            "Validation and edge-case tests were generated for common e-commerce failure cases.",
            "Regression tests were generated to prevent known bugs from returning.",
            "Security validation tests were generated using SecurityReport_v1.json.",
            "Test traceability mapping was added for requirement, API, module, and security validation coverage."
        ]

        if summary.failed > 0:
            recommendations.insert(
                0,
                "Some generated tests failed. Review pytest stdout/stderr in TestReport_v1.json."
            )

        if summary.skipped > 0:
            recommendations.append(
                "Some tests were skipped. If security validation tests were skipped, run the Security Agent before the Testing Agent."
            )

        return TestReport(
            run_id=run_id,
            stage="testing",
            version=version,
            target_path=target_path,
            generated_tests_path=generated_tests_path,
            generated_test_files=generated_test_files,
            regression_tests_path=regression_tests_path,
            regression_test_cases=regression_test_cases,
            security_validation_tests_path=security_validation_tests_path,
            security_validation_cases=security_validation_cases,
            traceability_summary=traceability_summary,
            pytest_run=pytest_result,
            summary=summary,
            test_cases=test_cases,
            execution_results=execution_results,
            metrics=metrics,
            recommendations=recommendations
        )