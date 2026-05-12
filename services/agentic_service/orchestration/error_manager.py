import json
from pathlib import Path

from states.system_state import WorkflowError


class ErrorManager:
    """
    Saves workflow errors to a separate log file.

    This is useful for debugging agent failures without only depending
    on terminal logs.
    """

    def __init__(self, output_dir: str = "outputs"):
        self.output_dir = Path(output_dir)

    def _error_path(self, run_id: str) -> Path:
        return self.output_dir / "runs" / run_id / "logs" / "workflow_errors.json"

    def append_error(
        self,
        run_id: str,
        stage: str,
        error_type: str,
        message: str,
    ) -> WorkflowError:
        """
        Appends one error to workflow_errors.json.
        """

        path = self._error_path(run_id)
        path.parent.mkdir(parents=True, exist_ok=True)

        if path.exists():
            errors = json.loads(path.read_text(encoding="utf-8"))
        else:
            errors = []

        error = WorkflowError(
            stage=stage,
            error_type=error_type,
            message=message,
        )

        errors.append(error.model_dump())

        path.write_text(
            json.dumps(errors, indent=2),
            encoding="utf-8",
        )

        return error