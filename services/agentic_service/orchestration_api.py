from fastapi import FastAPI, HTTPException

from orchestration.stage_service import StageService

app = FastAPI(
    title="AutoForge Agentic Service API",
    description="Single-service multi-agent system for E-commerce SDLC automation.",
    version="1.0.0",
)

stage_service = StageService(output_dir="outputs")


@app.get("/health")
def health():
    """
    Simple health check endpoint.
    """

    return {
        "status": "ok",
        "service": "autoforge-agentic-service",
    }


# -------------------------------------------------------------------
# Orchestration endpoints
# -------------------------------------------------------------------


@app.post("/runs")
def create_run(payload: dict):
    """
    Creates a new AutoForge workflow run.

    Example payload:
    {
      "project_name": "AutoForge Shop"
    }
    """

    try:
        state = stage_service.create_run(
            project_name=payload.get("project_name"),
            run_id=payload.get("run_id"),
        )

        return state.model_dump()

    except Exception as error:
        raise HTTPException(status_code=500, detail=str(error))


@app.get("/runs/{run_id}")
def get_run_status(run_id: str):
    """
    Returns current workflow state and approval state.
    """

    try:
        return stage_service.get_status(run_id)

    except Exception as error:
        raise HTTPException(status_code=404, detail=str(error))


@app.get("/runs/{run_id}/artifacts")
def get_run_artifacts(run_id: str):
    """
    Returns all artifacts registered for this run.
    """

    try:
        return stage_service.get_artifacts(run_id)

    except Exception as error:
        raise HTTPException(status_code=404, detail=str(error))


@app.post("/runs/{run_id}/stages/{stage}/generate")
async def generate_stage(run_id: str, stage: str, payload: dict):
    """
    Generates a workflow stage.

    Supported stages now:
    - requirements
    - domain
    """

    try:
        return await stage_service.generate_stage(
            run_id=run_id,
            stage=stage,
            payload=payload,
        )

    except Exception as error:
        raise HTTPException(status_code=500, detail=str(error))


@app.post("/runs/{run_id}/stages/{stage}/approve")
def approve_stage(run_id: str, stage: str, payload: dict):
    """
    Approves a stage version.

    Example:
    {
      "version": "v1",
      "comment": "Approved"
    }
    """

    try:
        return stage_service.approve_stage(
            run_id=run_id,
            stage=stage,
            payload=payload,
        )

    except Exception as error:
        raise HTTPException(status_code=500, detail=str(error))


@app.post("/runs/{run_id}/stages/{stage}/reject")
def reject_stage(run_id: str, stage: str, payload: dict):
    """
    Rejects a stage version.

    Example:
    {
      "version": "v1",
      "comment": "Add product search requirement"
    }
    """

    try:
        return stage_service.reject_stage(
            run_id=run_id,
            stage=stage,
            payload=payload,
        )

    except Exception as error:
        raise HTTPException(status_code=500, detail=str(error))


@app.post("/runs/{run_id}/stages/{stage}/revise")
async def revise_stage(run_id: str, stage: str, payload: dict):
    """
    Revises a stage.

    Currently supported:
    - requirements

    Example:
    {
      "current_version": "v1",
      "change_request": "Add product search and filtering."
    }
    """

    try:
        return await stage_service.revise_stage(
            run_id=run_id,
            stage=stage,
            payload=payload,
        )

    except Exception as error:
        raise HTTPException(status_code=500, detail=str(error))


# -------------------------------------------------------------------
# Optional legacy/direct endpoints can be added later.
# For now, we keep this API clean to avoid importing unstable agents.
# -------------------------------------------------------------------