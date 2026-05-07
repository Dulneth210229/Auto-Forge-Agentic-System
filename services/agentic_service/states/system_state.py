from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


def utc_now() -> str:
    """
    Returns current UTC time as an ISO string.

    We store timestamps in UTC because workflow runs may later be executed
    on different machines, servers, or CI/CD environments.
    """
    return datetime.now(timezone.utc).isoformat()


class ArtifactRecord(BaseModel):
    """
    Represents one generated artifact in the AutoForge workflow.

    Example:
    - SRS_v1.json
    - SRS_v1.md
    - DomainPack_v1.json
    - DomainPack_v1.md
    """

    stage: str
    version: str
    artifact_type: str
    path: str
    status: str = "pending_approval"


class WorkflowError(BaseModel):
    """
    Stores workflow errors in a structured way.

    This is better than only relying on terminal tracebacks because
    the UI/API can later show meaningful error messages to the user.
    """

    stage: str
    error_type: str
    message: str
    timestamp: str = Field(default_factory=utc_now)


class WorkflowState(BaseModel):
    """
    Main workflow state object.

    This file becomes:
    outputs/runs/RUN-0001/workflow_state.json

    The orchestrator reads and updates this file after every stage.
    """

    run_id: str
    project_name: Optional[str] = None

    current_stage: str = "RUN_CREATED"
    pending_approval_stage: Optional[str] = None

    approved_stages: List[str] = Field(default_factory=list)

    latest_versions: Dict[str, Optional[str]] = Field(
        default_factory=lambda: {
            "requirements": None,
            "domain": None,
            "architecture": None,
            "uiux": None,
            "code": None,
            "tests": None,
            "security": None,
            "export": None,
        }
    )

    artifacts: List[ArtifactRecord] = Field(default_factory=list)

    messages: List[str] = Field(default_factory=list)
    errors: List[WorkflowError] = Field(default_factory=list)

    traceability_links: List[Dict[str, Any]] = Field(default_factory=list)

    next_action: Optional[str] = "Generate the SRS using the Requirement Agent."

    created_at: str = Field(default_factory=utc_now)
    updated_at: str = Field(default_factory=utc_now)

    def touch(self) -> None:
        """
        Updates the modified timestamp.

        Call this before saving the workflow state.
        """
        self.updated_at = utc_now()