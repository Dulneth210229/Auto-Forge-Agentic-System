from typing import List, Literal
from pydantic import BaseModel, Field


class TestCase(BaseModel):
    """
    Represents one QA test case.
    """

    test_id: str
    title: str
    description: str
    test_type: Literal[
        "unit",
        "integration",
        "api",
        "ui",
        "security_validation",
        "smoke",
        "regression"
    ]
    target_module: str
    target_file: str
    related_requirement_id: str = ""
    expected_result: str


class TestExecutionResult(BaseModel):
    """
    Represents the execution result of one test case or generated pytest test.
    """

    test_id: str
    status: Literal["passed", "failed", "skipped", "not_run"]
    message: str = ""
    duration_ms: int = Field(default=0, ge=0)


class GeneratedTestFile(BaseModel):
    """
    Represents one generated pytest file.
    """

    file_name: str
    file_path: str
    test_type: Literal[
        "smoke",
        "unit",
        "integration",
        "api",
        "security_validation",
        "regression"
    ]
    description: str


class RegressionTestCase(BaseModel):
    """
    Represents one regression test scenario.
    """

    regression_id: str
    title: str
    description: str
    related_requirement_id: str = ""
    related_module: str
    expected_behavior: str


class SecurityValidationCase(BaseModel):
    """
    Represents one security validation scenario.

    These scenarios are generated from or aligned with SecurityReport_v1.json.
    """

    validation_id: str
    title: str
    description: str
    related_security_artifact: str
    expected_behavior: str


class PytestRunResult(BaseModel):
    """
    Represents the overall pytest execution result.
    """

    exit_code: int
    status: Literal["passed", "failed", "error"]
    duration_ms: int = Field(default=0, ge=0)
    stdout: str = ""
    stderr: str = ""


class TestSummary(BaseModel):
    """
    Summary counts for the Testing Agent.
    """

    total_tests: int = 0
    passed: int = 0
    failed: int = 0
    skipped: int = 0
    not_run: int = 0


class TestMetrics(BaseModel):
    """
    QA evaluation metrics.
    """

    test_coverage: float = 0.0
    pass_rate: float = 0.0
    execution_efficiency: float = 0.0


class TestReport(BaseModel):
    """
    Main machine-readable Test Report schema.
    Saved as TestReport_v1.json.
    """

    run_id: str
    stage: Literal["testing"] = "testing"
    version: str
    target_path: str

    generated_tests_path: str = ""
    generated_test_files: List[GeneratedTestFile] = []

    regression_tests_path: str = ""
    regression_test_cases: List[RegressionTestCase] = []

    security_validation_tests_path: str = ""
    security_validation_cases: List[SecurityValidationCase] = []

    pytest_run: PytestRunResult | None = None

    summary: TestSummary
    test_cases: List[TestCase]
    execution_results: List[TestExecutionResult]
    metrics: TestMetrics
    recommendations: List[str] = []