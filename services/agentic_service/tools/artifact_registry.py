import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Any, List


class ArtifactRegistry:
    """
    Stores generated AutoForge artifacts in one run-level metadata file.

    Example metadata path:
        outputs/runs/RUN-0001/run_metadata.json

    This allows future agents to find previous outputs automatically.
    For example:
        Coder Agent can find SecurityReport_v1.json
        Security Agent can find generated_app/
        Orchestrator can show artifact history
    """

    def __init__(self, output_root: str = "outputs"):
        self.output_root = Path(output_root)

    def get_metadata_path(self, run_id: str) -> Path:
        """
        Return metadata file path for a given run.
        """

        return self.output_root / "runs" / run_id / "run_metadata.json"

    def load_metadata(self, run_id: str) -> Dict[str, Any]:
        """
        Load existing metadata file.

        If metadata does not exist, create a new empty structure.
        """

        metadata_path = self.get_metadata_path(run_id)

        if not metadata_path.exists():
            return {
                "run_id": run_id,
                "created_at": datetime.now(timezone.utc).isoformat(),
                "updated_at": datetime.now(timezone.utc).isoformat(),
                "artifacts": []
            }

        return json.loads(metadata_path.read_text(encoding="utf-8"))

    def save_metadata(self, run_id: str, metadata: Dict[str, Any]) -> str:
        """
        Save metadata file.
        """

        metadata_path = self.get_metadata_path(run_id)
        metadata_path.parent.mkdir(parents=True, exist_ok=True)

        metadata["updated_at"] = datetime.now(timezone.utc).isoformat()

        metadata_path.write_text(
            json.dumps(metadata, indent=2),
            encoding="utf-8"
        )

        return str(metadata_path)

    def register_artifact(
        self,
        run_id: str,
        stage: str,
        version: str,
        artifact_type: str,
        path: str,
        format: str,
        description: str = ""
    ) -> str:
        """
        Register one generated artifact.

        If an artifact with the same stage, version, type and path already exists,
        it will not be duplicated.
        """

        metadata = self.load_metadata(run_id)

        artifact = {
            "stage": stage,
            "version": version,
            "type": artifact_type,
            "format": format,
            "path": path,
            "description": description,
            "registered_at": datetime.now(timezone.utc).isoformat()
        }

        existing_artifacts: List[Dict[str, Any]] = metadata.get("artifacts", [])

        is_duplicate = any(
            item.get("stage") == artifact["stage"]
            and item.get("version") == artifact["version"]
            and item.get("type") == artifact["type"]
            and item.get("path") == artifact["path"]
            for item in existing_artifacts
        )

        if not is_duplicate:
            existing_artifacts.append(artifact)

        metadata["artifacts"] = existing_artifacts

        return self.save_metadata(run_id, metadata)

    def register_many(
        self,
        run_id: str,
        artifacts: List[Dict[str, str]]
    ) -> str:
        """
        Register multiple artifacts at once.
        """

        metadata_path = ""

        for artifact in artifacts:
            metadata_path = self.register_artifact(
                run_id=run_id,
                stage=artifact["stage"],
                version=artifact["version"],
                artifact_type=artifact["type"],
                path=artifact["path"],
                format=artifact["format"],
                description=artifact.get("description", "")
            )

        return metadata_path

    def find_latest_artifact(
        self,
        run_id: str,
        stage: str,
        artifact_type: str
    ) -> Dict[str, Any] | None:
        """
        Find the latest artifact for a given stage and type.
        """

        metadata = self.load_metadata(run_id)

        matching = [
            artifact for artifact in metadata.get("artifacts", [])
            if artifact.get("stage") == stage
            and artifact.get("type") == artifact_type
        ]

        if not matching:
            return None

        return matching[-1]