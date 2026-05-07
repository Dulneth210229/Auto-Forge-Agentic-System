from typing import List

from states.system_state import ArtifactRecord, WorkflowState


class ArtifactRegistry:
    """
    Helper class for managing artifact records inside WorkflowState.

    The actual files are created by each agent.
    This registry only stores metadata about those files.
    """

    @staticmethod
    def add_artifact(
        state: WorkflowState,
        stage: str,
        version: str,
        artifact_type: str,
        path: str,
        status: str = "pending_approval",
    ) -> WorkflowState:
        """
        Adds one artifact record to workflow state.
        """

        record = ArtifactRecord(
            stage=stage,
            version=version,
            artifact_type=artifact_type,
            path=path,
            status=status,
        )

        state.artifacts.append(record)
        state.touch()

        return state

    @staticmethod
    def get_stage_artifacts(
        state: WorkflowState,
        stage: str,
        version: str | None = None,
    ) -> List[ArtifactRecord]:
        """
        Returns artifacts for a given stage.

        If version is provided, only that version is returned.
        """

        results = []

        for artifact in state.artifacts:
            if artifact.stage != stage:
                continue

            if version is not None and artifact.version != version:
                continue

            results.append(artifact)

        return results

    @staticmethod
    def update_artifact_status(
        state: WorkflowState,
        stage: str,
        version: str,
        status: str,
    ) -> WorkflowState:
        """
        Updates all artifacts belonging to a stage/version.

        Example:
        SRS_v1.json and SRS_v1.md both become approved.
        """

        for artifact in state.artifacts:
            if artifact.stage == stage and artifact.version == version:
                artifact.status = status

        state.touch()

        return state