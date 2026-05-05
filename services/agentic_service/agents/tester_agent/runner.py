import os
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

    Step 4 improvement:
    - Collect individual pytest test node IDs.
    - Execute pytest.
    - Convert each collected test into one TestExecutionResult.
    - Count passed/failed/skipped tests individually.
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

        env = os.environ.copy()

        # Prevent third-party pytest plugins from causing issues inside FastAPI subprocesses.
        env["PYTEST_DISABLE_PLUGIN_AUTOLOAD"] = "1"

        start_time = time.perf_counter()

        try:
            completed = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "pytest",
                    str(test_path),
                    "-q",
                    "--tb=short",
                    "--disable-warnings"
                ],
                capture_output=True,
                text=True,
                cwd=Path.cwd(),
                env=env,
                timeout=60
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

        except subprocess.TimeoutExpired as error:
            duration_ms = int((time.perf_counter() - start_time) * 1000)

            return PytestRunResult(
                exit_code=-1,
                status="error",
                duration_ms=duration_ms,
                stdout=error.stdout or "",
                stderr="Pytest execution timed out after 60 seconds."
            )

        except Exception as error:
            duration_ms = int((time.perf_counter() - start_time) * 1000)

            return PytestRunResult(
                exit_code=-2,
                status="error",
                duration_ms=duration_ms,
                stdout="",
                stderr=f"Pytest execution failed: {error}"
            )

    def collect_test_ids(self, generated_tests_path: str) -> List[str]:
        """
        Collect individual pytest test IDs using pytest --collect-only.

        Example returned ID:
        outputs/runs/RUN-0001/tests/v1/generated_tests/test_project_structure.py::test_target_project_folder_exists
        """

        test_path = Path(generated_tests_path)

        if not test_path.exists():
            raise FileNotFoundError(
                f"Generated tests folder does not exist: {generated_tests_path}"
            )

        env = os.environ.copy()
        env["PYTEST_DISABLE_PLUGIN_AUTOLOAD"] = "1"

        completed = subprocess.run(
            [
                sys.executable,
                "-m",
                "pytest",
                str(test_path),
                "--collect-only",
                "-q"
            ],
            capture_output=True,
            text=True,
            cwd=Path.cwd(),
            env=env,
            timeout=60
        )

        output = f"{completed.stdout}\n{completed.stderr}"

        test_ids: List[str] = []

        for line in output.splitlines():
            clean_line = line.strip()

            if not clean_line:
                continue

            if "::" not in clean_line:
                continue

            if clean_line.startswith("<"):
                continue

            test_ids.append(clean_line)

        return test_ids

    def build_execution_results(
        self,
        pytest_result: PytestRunResult,
        collected_test_ids: List[str]
    ) -> List[TestExecutionResult]:
        """
        Build one execution result per collected pytest test.

        Step 4 strategy:
        - If pytest passed, mark all collected tests as passed.
        - If pytest failed, mark tests listed in FAILED lines as failed.
        - Other collected tests are marked as passed unless pytest had a process-level error.
        - If pytest crashed before collection, return one PYTEST-RUN-001 failure.
        """

        if not collected_test_ids:
            return [
                TestExecutionResult(
                    test_id="PYTEST-RUN-001",
                    status="passed" if pytest_result.status == "passed" else "failed",
                    message=self._build_summary_message(pytest_result),
                    duration_ms=pytest_result.duration_ms
                )
            ]

        failed_test_ids = self._extract_failed_test_ids(pytest_result)

        results: List[TestExecutionResult] = []

        duration_per_test = 0

        if collected_test_ids:
            duration_per_test = int(pytest_result.duration_ms / len(collected_test_ids))

        for test_id in collected_test_ids:
            if pytest_result.status == "error":
                status = "failed"
                message = self._build_summary_message(pytest_result)
            elif test_id in failed_test_ids:
                status = "failed"
                message = "Test failed. See pytest stdout/stderr for details."
            else:
                status = "passed"
                message = "Test passed."

            results.append(
                TestExecutionResult(
                    test_id=test_id,
                    status=status,
                    message=message,
                    duration_ms=duration_per_test
                )
            )

        return results

    def extract_counts(
        self,
        pytest_result: PytestRunResult,
        execution_results: List[TestExecutionResult]
    ) -> dict:
        """
        Count passed/failed/skipped/not_run from execution_results.
        """

        passed = sum(1 for result in execution_results if result.status == "passed")
        failed = sum(1 for result in execution_results if result.status == "failed")
        skipped = sum(1 for result in execution_results if result.status == "skipped")
        not_run = sum(1 for result in execution_results if result.status == "not_run")

        total = passed + failed + skipped + not_run

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
            "not_run": not_run
        }

    def _status_from_exit_code(self, exit_code: int) -> str:
        """
        Pytest exit code:
        0 = all tests passed
        1 = tests failed
        other = pytest/config/process error
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
            return (
                f"Pytest exited with code {pytest_result.exit_code} "
                f"and produced no stdout/stderr."
            )

        lines = [line.strip() for line in output.splitlines() if line.strip()]

        for line in reversed(lines):
            lowered = line.lower()

            if (
                "passed" in lowered
                or "failed" in lowered
                or "error" in lowered
                or "collected" in lowered
            ):
                return line

        return lines[-1]

    def _extract_failed_test_ids(self, pytest_result: PytestRunResult) -> set[str]:
        """
        Extract failed test node IDs from pytest output.

        Example pytest line:
        FAILED path/to/test_file.py::test_name - AssertionError
        """

        output = f"{pytest_result.stdout}\n{pytest_result.stderr}"

        failed_test_ids: set[str] = set()

        for line in output.splitlines():
            clean_line = line.strip()

            if not clean_line.startswith("FAILED "):
                continue

            # Remove "FAILED "
            failed_part = clean_line.replace("FAILED ", "", 1)

            # Keep only the node id before " - "
            failed_node_id = failed_part.split(" - ")[0].strip()

            if failed_node_id:
                failed_test_ids.add(failed_node_id)

        return failed_test_ids