import re
import subprocess
import sys
import time
from pathlib import Path
from typing import List

from agents.tester_agent.schemas import (
    PytestRunResult,
    TestExecutionResult
)


class PytestRunner:
    """
    Runs generated pytest files and converts pytest output into report data.
    """

    def run_tests(self, generated_tests_path: str) -> PytestRunResult:
        """
        Execute pytest for the generated_tests folder.
        """

        test_path = Path(generated_tests_path)

        if not test_path.exists():
            raise FileNotFoundError(
                f"Generated tests folder does not exist: {generated_tests_path}"
            )

        start_time = time.perf_counter()

        completed = subprocess.run(
            [
                sys.executable,
                "-m",
                "pytest",
                str(test_path),
                "-q"
            ],
            capture_output=True,
            text=True
        )

        duration_ms = int((time.perf_counter() - start_time) * 1000)

        status = self._status_from_exit_code(completed.returncode)

        return PytestRunResult(
            exit_code=completed.returncode,
            status=status,
            duration_ms=duration_ms,
            stdout=completed.stdout,
            stderr=completed.stderr
        )

    def build_execution_results(
        self,
        pytest_result: PytestRunResult
    ) -> List[TestExecutionResult]:
        """
        Convert overall pytest output into simple execution result records.

        Step 3 keeps parsing simple:
        - One result for overall pytest run.
        - Detailed individual test parsing will be improved in Step 4.
        """

        message = self._build_summary_message(pytest_result)

        return [
            TestExecutionResult(
                test_id="PYTEST-RUN-001",
                status="passed" if pytest_result.status == "passed" else "failed",
                message=message,
                duration_ms=pytest_result.duration_ms
            )
        ]

    def _status_from_exit_code(self, exit_code: int) -> str:
        """
        Pytest exit code:
        0 = all tests passed
        1 = tests failed
        Other = execution/config error
        """

        if exit_code == 0:
            return "passed"

        if exit_code == 1:
            return "failed"

        return "error"

    def _build_summary_message(self, pytest_result: PytestRunResult) -> str:
        """
        Extract a readable message from pytest stdout/stderr.
        """

        output = f"{pytest_result.stdout}\n{pytest_result.stderr}".strip()

        if not output:
            return "Pytest completed with no output."

        lines = [line.strip() for line in output.splitlines() if line.strip()]

        # Prefer pytest final summary line.
        for line in reversed(lines):
            if "passed" in line or "failed" in line or "error" in line:
                return line

        return lines[-1]

    def extract_counts(self, pytest_result: PytestRunResult) -> dict:
        """
        Extract basic passed/failed/skipped counts from pytest output.
        """

        output = f"{pytest_result.stdout}\n{pytest_result.stderr}"

        passed = self._extract_count(output, "passed")
        failed = self._extract_count(output, "failed")
        skipped = self._extract_count(output, "skipped")
        errors = self._extract_count(output, "error")

        # Treat pytest errors as failed for report summary.
        failed += errors

        total = passed + failed + skipped

        if total == 0 and pytest_result.status == "passed":
            total = 1
            passed = 1

        if total == 0 and pytest_result.status in ["failed", "error"]:
            total = 1
            failed = 1

        return {
            "total": total,
            "passed": passed,
            "failed": failed,
            "skipped": skipped,
            "not_run": 0
        }

    def _extract_count(self, output: str, keyword: str) -> int:
        """
        Extract count from text such as:
        '7 passed'
        '1 failed'
        '2 skipped'
        """

        pattern = rf"(\\d+)\\s+{keyword}"
        match = re.search(pattern, output)

        if not match:
            return 0

        return int(match.group(1))