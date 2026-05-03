from typing import List, Literal
from pydantic import BaseModel, Field


class TestCase(BaseModel):
    """
    Represents one QA test case.
    """

    test_id: str
    title: str
    description: str
    test_type: Literal["unit", "integration", "api", "ui", "security_validation"]
    target_module: str
    target_file: str
    related_requirement_id: str = ""
    expected_result: str


class TestExecutionResult(BaseModel):
    """
    Represents the execution result of one test case.
    """

    test_id: str
    status: Literal["passed", "failed", "skipped", "not_run"]
    message: str = ""
    duration_ms: int = Field(default=0, ge=0)


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
    summary: TestSummary
    test_cases: List[TestCase]
    execution_results: List[TestExecutionResult]
    metrics: TestMetrics
    recommendations: List[str] = []