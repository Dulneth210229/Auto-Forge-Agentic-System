import json
from pathlib import Path
from typing import Optional

from states.system_state import WorkflowState


class RunManager:
    """
    Creates and manages AutoForge workflow runs.

    A run is one complete attempt to generate artifacts for a project.

    Example:
    outputs/runs/RUN-0001/
    """

    def __init__(self, output_dir: str = "outputs"):
        self.output_dir = Path(output_dir)
        self.runs_dir = self.output_dir / "runs"
        self.runs_dir.mkdir(parents=True, exist_ok=True)

    def _state_path(self, run_id: str) -> Path:
        """
        Returns workflow_state.json path for a run.
        """

        return self.runs_dir / run_id / "workflow_state.json"

    def generate_next_run_id(self) -> str:
        """
        Creates the next run id.

        Example:
        if RUN-0001 exists, next is RUN-0002.
        """

        existing_numbers = []

        for item in self.runs_dir.iterdir():
            if not item.is_dir():
                continue

            if item.name.startswith("RUN-"):
                try:
                    number = int(item.name.replace("RUN-", ""))
                    existing_numbers.append(number)
                except ValueError:
                    continue

        next_number = max(existing_numbers, default=0) + 1

        return f"RUN-{next_number:04d}"

    def create_run(
        self,
        project_name: Optional[str] = None,
        run_id: Optional[str] = None,
    ) -> WorkflowState:
        """
        Creates a new run folder and initial workflow_state.json.
        """

        final_run_id = run_id or self.generate_next_run_id()

        run_dir = self.runs_dir / final_run_id
        run_dir.mkdir(parents=True, exist_ok=True)

        # Create standard folders for future stages.
        for folder in [
            "approvals",
            "logs",
            "srs",
            "domain",
            "architecture",
            "uiux",
            "code",
            "tests",
            "security",
            "exports",
        ]:
            (run_dir / folder).mkdir(parents=True, exist_ok=True)

        state = WorkflowState(
            run_id=final_run_id,
            project_name=project_name,
            current_stage="RUN_CREATED",
            next_action="Generate requirements using the Requirement Agent.",
        )

        self.save_state(state)

        return state

    def load_state(self, run_id: str) -> WorkflowState:
        """
        Loads workflow_state.json.
        """

        path = self._state_path(run_id)

        if not path.exists():
            raise FileNotFoundError(f"Workflow state not found for run_id: {run_id}")

        data = json.loads(path.read_text(encoding="utf-8"))

        return WorkflowState.model_validate(data)

    def save_state(self, state: WorkflowState) -> WorkflowState:
        """
        Saves workflow_state.json.
        """

        state.touch()

        path = self._state_path(state.run_id)
        path.parent.mkdir(parents=True, exist_ok=True)

        path.write_text(
            json.dumps(state.model_dump(), indent=2),
            encoding="utf-8",
        )

        return state