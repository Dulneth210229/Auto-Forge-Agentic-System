import json
from pathlib import Path
from typing import Optional

from states.system_state import utc_now


class ApprovalManager:
    """
    Manages human-in-the-loop approval decisions.

    Approval data is stored separately from workflow_state.json so that
    it is easy to audit approval history.
    """

    def __init__(self, output_dir: str = "outputs"):
        self.output_dir = Path(output_dir)

    def _approval_path(self, run_id: str) -> Path:
        """
        Returns approval_state.json path for a run.
        """

        return self.output_dir / "runs" / run_id / "approvals" / "approval_state.json"

    def _load(self, run_id: str) -> dict:
        """
        Loads approval state.

        If approval_state.json does not exist yet, return empty dict.
        """

        path = self._approval_path(run_id)

        if not path.exists():
            return {}

        return json.loads(path.read_text(encoding="utf-8"))

    def _save(self, run_id: str, data: dict) -> None:
        """
        Saves approval state.
        """

        path = self._approval_path(run_id)
        path.parent.mkdir(parents=True, exist_ok=True)

        path.write_text(
            json.dumps(data, indent=2),
            encoding="utf-8",
        )

    def set_pending(
        self,
        run_id: str,
        stage: str,
        version: str,
        comment: Optional[str] = None,
    ) -> dict:
        """
        Marks an artifact version as pending approval.
        """

        data = self._load(run_id)

        data.setdefault(stage, {})
        data[stage][version] = {
            "status": "pending",
            "comment": comment,
            "timestamp": utc_now(),
        }

        self._save(run_id, data)
        return data

    def approve(
        self,
        run_id: str,
        stage: str,
        version: str,
        comment: Optional[str] = None,
    ) -> dict:
        """
        Marks an artifact version as approved.
        """

        data = self._load(run_id)

        data.setdefault(stage, {})
        data[stage][version] = {
            "status": "approved",
            "comment": comment,
            "timestamp": utc_now(),
        }

        self._save(run_id, data)
        return data

    def reject(
        self,
        run_id: str,
        stage: str,
        version: str,
        comment: Optional[str] = None,
    ) -> dict:
        """
        Marks an artifact version as rejected.
        """

        data = self._load(run_id)

        data.setdefault(stage, {})
        data[stage][version] = {
            "status": "rejected",
            "comment": comment,
            "timestamp": utc_now(),
        }

        self._save(run_id, data)
        return data

    def is_approved(self, run_id: str, stage: str, version: str) -> bool:
        """
        Checks whether a stage/version is approved.
        """

        data = self._load(run_id)

        return (
            data.get(stage, {})
            .get(version, {})
            .get("status") == "approved"
        )

    def get_approval_state(self, run_id: str) -> dict:
        """
        Returns all approval data for one run.
        """

        return self._load(run_id)