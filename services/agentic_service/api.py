import logging
from typing import Optional
import threading
from datetime import datetime

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from agents.requirement_agent.agent import RequirementAgent
from agents.domain_agent.agent import DomainAgent
from agents.architect_agent.agent import ArchitectAgent
from agents.uiux_agent.agent import UIUXAgent
from agents.coder_agent.agent import CoderAgent
from agents.security_agent.agent import SecurityAgent
from agents.tester_agent.agent import TesterAgent
from tools.llm.provider import OllamaProvider
from agents.architect_agent.agent import ArchitectAgent

uiux_agent = UIUXAgent(llm_provider=OllamaProvider())


logger = logging.getLogger(__name__)


app = FastAPI(
    title="AutoForge Agentic Service API",
    description="Single-service multi-agent system for E-commerce SDLC automation.",
    version="1.0.0"
)


# ---------------------------------------------------------
# Agent instances
# ---------------------------------------------------------

requirement_agent = RequirementAgent(llm_provider=OllamaProvider())
domain_agent = DomainAgent(llm_provider=OllamaProvider())
architect_agent = ArchitectAgent()
coder_agent = CoderAgent(llm_provider=OllamaProvider())
security_agent = SecurityAgent(output_root="outputs")
tester_agent = TesterAgent(output_root="outputs")


# ---------------------------------------------------------
# Request / Response Models
# ---------------------------------------------------------

class SecurityRunRequest(BaseModel):
    """
    Request body for running the Security Agent.
    """

    run_id: str = Field(
        default="RUN-0001",
        description="AutoForge run ID"
    )

    version: str = Field(
        default="v1",
        description="Artifact version"
    )

    target_path: str = Field(
        default="./sample_ecommerce_app",
        description="Target source code folder to scan"
    )

    enable_llm: bool = Field(
        default=False,
        description="Enable Ollama LLM-assisted secure code review"
    )


class SecurityRunResponse(BaseModel):
    """
    Response body after running the Security Agent.
    """

    run_id: str
    stage: str
    version: str
    target_path: Optional[str]
    llm_enabled: bool

    json_path: str
    markdown_path: str
    summary_pack_json_path: str
    summary_pack_markdown_path: str
    metadata_path: str

    summary: dict
    dependency_vulnerabilities_count: int
    llm_findings_count: int
    deduplication: dict
    security_gate: dict
    traceability_mapped: bool
    fix_suggestions_count: int


class TestingRunRequest(BaseModel):
    """
    Request body for running the Testing / QA Agent.
    """

    run_id: str = Field(
        default="RUN-0001",
        description="AutoForge run ID"
    )

    version: str = Field(
        default="v1",
        description="Artifact version"
    )

    target_path: str = Field(
        default="./sample_ecommerce_app",
        description="Target source code folder to test"
    )


class TestingRunResponse(BaseModel):
    """
    Response body after running the Testing / QA Agent.
    """

    run_id: str
    stage: str
    version: str
    target_path: str

    json_path: str
    markdown_path: str
    summary_pack_json_path: str
    summary_pack_markdown_path: str
    metadata_path: str

    generated_tests_path: str
    generated_test_files_count: int

    pytest_status: str
    pytest_exit_code: int

    summary: dict
    metrics: dict

    traceability_summary: dict

    quality_gate: dict


class CoderGenerateRequest(BaseModel):
    """
    Request body for the Coder Agent code generation.
    """

    run_id: str = Field(
        default="RUN-0001",
        description="AutoForge run ID"
    )

    srs_version: str = Field(
        default="v1",
        description="Source SRS version (e.g., v1, v2)"
    )

    code_version: str = Field(
        default="v1",
        description="Target code version to generate (e.g., v1, v2)"
    )


class CoderGenerateResponse(BaseModel):
    """
    Response body after code generation.
    """

    status: str
    run_id: str
    code_version: str
    source_srs_version: str
    manifest_path: str
    output_dir: str
    generated_file_count: int


# ---------------------------------------------------------
# Health Endpoint
# ---------------------------------------------------------

@app.get("/health")
def health():
    return {
        "status": "ok",
        "service": "autoforge-agentic-service"
    }


# ---------------------------------------------------------
# Requirement Agent Endpoints
# ---------------------------------------------------------

@app.post("/requirements/intake/validate")
def validate_intake(payload: dict):
    questions = requirement_agent.get_clarification_questions(payload)

    if questions:
        return {
            "valid": False,
            "clarification_required": True,
            "questions": questions
        }

    intake = requirement_agent.validate_intake(payload)

    return {
        "valid": True,
        "clarification_required": False,
        "intake": intake.model_dump()
    }


@app.post("/requirements/srs/generate")
async def generate_srs(payload: dict):
    run_id = payload.get("run_id", "RUN-0001")
    version = payload.get("version", "v1")
    intake = payload.get("intake", payload)

    result = await requirement_agent.generate_srs(
        intake_data=intake,
        run_id=run_id,
        version=version
    )

    return result


@app.post("/requirements/srs/revise")
async def revise_srs(payload: dict):
    result = await requirement_agent.revise_srs(
        run_id=payload["run_id"],
        current_version=payload["current_version"],
        new_version=payload["new_version"],
        change_request=payload["change_request"]
    )

    return result


# ---------------------------------------------------------
# Domain Agent Endpoints
# ---------------------------------------------------------

@app.post("/domain/knowledge/ingest")
def ingest_domain_knowledge(payload: dict):
    result = domain_agent.ingest_domain_knowledge(
        file_path=payload.get(
            "file_path",
            "knowledge/ecommerce_domain_knowledge.txt"
        ),
        vector_store_type=payload.get("vector_store_type", "faiss")
    )

    return result


@app.post("/domain/pack/generate")
async def generate_domain_pack(payload: dict):
    result = await domain_agent.generate_domain_pack(
        run_id=payload.get("run_id", "RUN-0001"),
        srs_version=payload.get("srs_version", "v1"),
        domain_version=payload.get("domain_version", "v1"),
        vector_store_type=payload.get("vector_store_type", "faiss"),
        top_k=payload.get("top_k", 6)
    )

    return result


# ---------------------------------------------------------
# Architect Agent Endpoints
# ---------------------------------------------------------

@app.post("/architecture/generate")
def generate_architecture(payload: dict):
    """
    Generate architecture artifacts from approved SRS and DomainPack.

    Required previous files:
    - outputs/runs/{run_id}/srs/{srs_version}/SRS_{srs_version}.json
    - outputs/runs/{run_id}/domain/{domain_version}/DomainPack_{domain_version}.json
    Generates fresh architecture artifacts from approved SRS and DomainPack.
    """

    try:
        result = architect_agent.generate_architecture(
            run_id=payload.get("run_id", "RUN-0001"),
            srs_version=payload.get("srs_version", "v1"),
            domain_version=payload.get("domain_version", "v1"),
            architecture_version=payload.get("architecture_version", "v1"),
            architecture_style=payload.get("architecture_style", "modular_monolith"),
            export_visuals=payload.get("export_visuals", True),
        )

        return result.model_dump()

    except FileNotFoundError as error:
        raise HTTPException(
            status_code=404,
            detail=str(error)
        )

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=f"Architect Agent failed: {error}"
        )


# ---------------------------------------------------------
# Coder Agent Endpoints
# ---------------------------------------------------------

@app.post("/coder/generate", response_model=CoderGenerateResponse)
async def generate_code(request: CoderGenerateRequest):
    """
    Generate runnable application code from the approved SRS using the Coder Agent.

    This endpoint:
    - reads SRS_{srs_version}.json
    - generates code files (backend, frontend, devops)
    - creates CodeManifest_{code_version}.json
    - returns generated file paths and count
    """
    
    try:
        logger.info(f"Coder Agent: Generating code for run_id={request.run_id}, srs_version={request.srs_version}, code_version={request.code_version}")
        
        result = await coder_agent.generate_code(
            run_id=request.run_id,
            srs_version=request.srs_version,
            code_version=request.code_version
        )
        
        logger.info(f"Coder Agent: Successfully generated {result.get('generated_file_count', 0)} files")
        return result
    
    except FileNotFoundError as error:
        logger.error(f"Coder Agent: SRS file not found - {error}")
        raise HTTPException(
            status_code=404,
            detail=f"SRS file not found: {error}"
        )
    
    except Exception as error:
        logger.error(f"Coder Agent: Unexpected error - {type(error).__name__}: {error}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Coder Agent failed: {type(error).__name__}: {error}"
        )

@app.post("/architecture/revise")
def revise_architecture(payload: dict):
    """
    Revises an existing architecture output version using user feedback.
    """

    result = architect_agent.revise_architecture(
        run_id=payload["run_id"],
        current_version=payload["current_version"],
        new_version=payload["new_version"],
        change_request=payload["change_request"],
        export_visuals=payload.get("export_visuals", True),
    )

    return result
# ---------------------------------------------------------
# UI/UX Agent Endpoints
# ---------------------------------------------------------

# ---------------------------------------------------------
# UI/UX Agent Endpoints - Manual Split Workflow
# ---------------------------------------------------------

@app.post("/uiux/srs/validate")
def validate_uiux_inputs(payload: dict):
    """
    Validates that the approved upstream artifacts required by UI/UX Agent exist.

    Required:
    - Approved SRS
    - Approved DomainPack
    - Approved Architecture output:
      SDS JSON, OpenAPI YAML, DBPack JSON
    """

    try:
        return uiux_agent.validate_approved_inputs(
            run_id=payload.get("run_id", "RUN-0001"),
            srs_version=payload.get("srs_version", "v1"),
            domain_version=payload.get("domain_version", "v1"),
            architecture_version=payload.get("architecture_version", "v1"),
        )

    except Exception as error:
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=500,
            detail=f"{type(error).__name__}: {str(error)}",
        )


@app.post("/uiux/plan/generate")
def generate_uiux_plan(payload: dict):
    """
    Step 1:
    Generates UI/UX plan only.

    Outputs:
    - uiux_plan_vX.json
    - user_flows_vX.json
    - user_flows_vX.mmd
    - user_flows_vX.png if render_images=True
    - trace_uiux_vX.json
    """

    try:
        return uiux_agent.generate_plan(
            run_id=payload.get("run_id", "RUN-0001"),
            srs_version=payload.get("srs_version", "v1"),
            domain_version=payload.get("domain_version", "v1"),
            architecture_version=payload.get("architecture_version", "v1"),
            uiux_version=payload.get("uiux_version", "v1"),
            include_admin=payload.get("include_admin", True),
            render_images=payload.get("render_images", True),
            user_prompt=payload.get("user_prompt"),
        )

    except Exception as error:
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=500,
            detail=f"{type(error).__name__}: {str(error)}",
        )


@app.post("/uiux/wireframes/generate-all")
def generate_all_uiux_wireframes(payload: dict):
    """
    Step 2:
    Generates all wireframes from the saved UI/UX plan.

    Important:
    - Run /uiux/plan/generate first.
    - This reads uiux_plan_vX.json.
    - Generates HTML/PNG screen by screen.
    - skip_existing=True avoids regenerating completed screens.
    """

    try:
        return uiux_agent.generate_all_wireframes(
            run_id=payload.get("run_id", "RUN-0001"),
            srs_version=payload.get("srs_version", "v1"),
            domain_version=payload.get("domain_version", "v1"),
            architecture_version=payload.get("architecture_version", "v1"),
            uiux_version=payload.get("uiux_version", "v1"),
            render_images=payload.get("render_images", True),
            user_prompt=payload.get("user_prompt"),
            fail_fast=payload.get("fail_fast", False),
            skip_existing=payload.get("skip_existing", True),
            max_screens=payload.get("max_screens"),
        )

    except Exception as error:
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=500,
            detail=f"{type(error).__name__}: {str(error)}",
        )


@app.post("/uiux/designpack/finalize")
def finalize_uiux_design_pack(payload: dict):
    """
    Step 3:
    Finalizes UIUXPack from existing artifacts.

    This endpoint does not call Ollama.
    """

    try:
        return uiux_agent.finalize_design_pack(
            run_id=payload.get("run_id", "RUN-0001"),
            srs_version=payload.get("srs_version", "v1"),
            domain_version=payload.get("domain_version", "v1"),
            architecture_version=payload.get("architecture_version", "v1"),
            uiux_version=payload.get("uiux_version", "v1"),
        )

    except Exception as error:
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=500,
            detail=f"{type(error).__name__}: {str(error)}",
        )


@app.post("/uiux/designpack/revise")
def revise_uiux_design_pack(payload: dict):
    """
    Revises UI/UX outputs as a new version.

    Used only when user gives a change request.
    """

    try:
        if not payload.get("change_request"):
            raise HTTPException(
                status_code=400,
                detail="change_request is required when revising UI/UX outputs.",
            )

        return uiux_agent.revise_design_pack(
            run_id=payload.get("run_id", "RUN-0001"),
            current_version=payload["current_version"],
            new_version=payload["new_version"],
            change_request=payload["change_request"],
            srs_version=payload.get("srs_version", "v1"),
            domain_version=payload.get("domain_version", "v1"),
            architecture_version=payload.get("architecture_version", "v1"),
            include_admin=payload.get("include_admin", True),
            render_images=payload.get("render_images", True),
            fail_fast=payload.get("fail_fast", False),
            skip_existing=payload.get("skip_existing", True),
            max_screens=payload.get("max_screens"),
        )

    except HTTPException:
        raise

    except Exception as error:
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=500,
            detail=f"{type(error).__name__}: {str(error)}",
        )


@app.post("/uiux/designpack/generate")
def generate_uiux_design_pack_legacy(payload: dict):
    """
    Legacy endpoint.

    This still works, but it runs the full workflow in one request.
    For best stability, use:
    - /orchestrator/uiux/run
    """

    try:
        return uiux_agent.generate_design_pack(
            run_id=payload.get("run_id", "RUN-0001"),
            srs_version=payload.get("srs_version", "v1"),
            domain_version=payload.get("domain_version", "v1"),
            architecture_version=payload.get("architecture_version", "v1"),
            uiux_version=payload.get("uiux_version", "v1"),
            include_admin=payload.get("include_admin", True),
            render_images=payload.get("render_images", True),
            user_prompt=payload.get("user_prompt"),
            change_request=payload.get("change_request"),
        )

    except Exception as error:
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=500,
            detail=f"{type(error).__name__}: {str(error)}",
        )


# ---------------------------------------------------------
# UI/UX Orchestrator - No public job_id
# ---------------------------------------------------------

uiux_jobs = {}
uiux_jobs_lock = threading.Lock()


def _now_iso() -> str:
    """
    Returns UTC timestamp string.
    """

    return datetime.utcnow().isoformat() + "Z"


def _uiux_job_key(run_id: str, uiux_version: str) -> str:
    """
    Internal key.

    User does not need to know this.
    User tracks using run_id + uiux_version.
    """

    return f"{run_id}:{uiux_version}"


def _set_uiux_job(run_id: str, uiux_version: str, updates: dict):
    """
    Thread-safe UI/UX job state update.
    """

    key = _uiux_job_key(run_id, uiux_version)

    with uiux_jobs_lock:
        current = uiux_jobs.get(key, {})
        current.update(updates)
        current["run_id"] = run_id
        current["uiux_version"] = uiux_version
        current["updated_at"] = _now_iso()
        uiux_jobs[key] = current


def _run_uiux_orchestrator_job(payload: dict):
    """
    Background UI/UX workflow.

    User-facing identity:
    - run_id
    - uiux_version

    Internal steps:
    1. Generate UI/UX plan
    2. Generate all wireframe HTML + PNG images
    3. Finalize UIUXPack
    """

    run_id = payload.get("run_id", "RUN-0001")
    srs_version = payload.get("srs_version", "v1")
    domain_version = payload.get("domain_version", "v1")
    architecture_version = payload.get("architecture_version", "v1")
    uiux_version = payload.get("uiux_version", "v1")
    include_admin = payload.get("include_admin", True)
    render_images = payload.get("render_images", True)
    user_prompt = payload.get("user_prompt")
    fail_fast = payload.get("fail_fast", False)
    skip_existing = payload.get("skip_existing", True)
    max_screens = payload.get("max_screens")

    try:
        _set_uiux_job(
            run_id,
            uiux_version,
            {
                "status": "running",
                "stage": "plan_generation",
                "message": "Generating UI/UX plan and user flow.",
                "started_at": _now_iso(),
                "payload": payload,
            },
        )

        plan_result = uiux_agent.generate_plan(
            run_id=run_id,
            srs_version=srs_version,
            domain_version=domain_version,
            architecture_version=architecture_version,
            uiux_version=uiux_version,
            include_admin=include_admin,
            render_images=render_images,
            user_prompt=user_prompt,
        )

        _set_uiux_job(
            run_id,
            uiux_version,
            {
                "status": "running",
                "stage": "wireframe_generation",
                "message": "Generating wireframe HTML and PNG images screen by screen.",
                "plan_result": plan_result,
            },
        )

        wireframe_result = uiux_agent.generate_all_wireframes(
            run_id=run_id,
            srs_version=srs_version,
            domain_version=domain_version,
            architecture_version=architecture_version,
            uiux_version=uiux_version,
            render_images=render_images,
            user_prompt=user_prompt,
            fail_fast=fail_fast,
            skip_existing=skip_existing,
            max_screens=max_screens,
        )

        _set_uiux_job(
            run_id,
            uiux_version,
            {
                "status": "running",
                "stage": "finalization",
                "message": "Finalizing UIUXPack JSON and Markdown.",
                "wireframe_result": wireframe_result,
            },
        )

        finalize_result = uiux_agent.finalize_design_pack(
            run_id=run_id,
            srs_version=srs_version,
            domain_version=domain_version,
            architecture_version=architecture_version,
            uiux_version=uiux_version,
            status="finalized",
        )

        final_status = "success"

        if wireframe_result.get("failed_count", 0) > 0:
            final_status = "partial_success"

        _set_uiux_job(
            run_id,
            uiux_version,
            {
                "status": final_status,
                "stage": "completed",
                "message": "UI/UX orchestration completed.",
                "finalize_result": finalize_result,
                "completed_at": _now_iso(),
            },
        )

    except Exception as error:
        import traceback
        traceback.print_exc()

        _set_uiux_job(
            run_id,
            uiux_version,
            {
                "status": "failed",
                "stage": "failed",
                "message": f"{type(error).__name__}: {str(error)}",
                "error": f"{type(error).__name__}: {str(error)}",
                "completed_at": _now_iso(),
            },
        )


@app.post("/orchestrator/uiux/run")
def run_uiux_orchestrator(payload: dict):
    """
    Starts the full UI/UX workflow in the background.

    No public job_id is required.
    User tracks progress using run_id + uiux_version.
    """

    run_id = payload.get("run_id", "RUN-0001")
    uiux_version = payload.get("uiux_version", "v1")

    _set_uiux_job(
        run_id,
        uiux_version,
        {
            "status": "queued",
            "stage": "queued",
            "message": "UI/UX orchestration queued.",
            "payload": payload,
            "created_at": _now_iso(),
        },
    )

    worker = threading.Thread(
        target=_run_uiux_orchestrator_job,
        args=(payload,),
        daemon=True,
    )

    worker.start()

    return {
        "status": "started",
        "run_id": run_id,
        "uiux_version": uiux_version,
        "message": "UI/UX workflow started in background.",
        "status_endpoint": f"/orchestrator/uiux/status?run_id={run_id}&uiux_version={uiux_version}",
    }


@app.get("/orchestrator/uiux/status")
def get_uiux_orchestrator_status(run_id: str, uiux_version: str):
    """
    Returns UI/UX orchestration status using run_id + uiux_version.

    No job_id is required.
    """

    key = _uiux_job_key(run_id, uiux_version)

    with uiux_jobs_lock:
        job = uiux_jobs.get(key)

    if not job:
        raise HTTPException(
            status_code=404,
            detail=f"No UI/UX orchestration found for run_id={run_id}, uiux_version={uiux_version}",
        )

    return job


# ---------------------------------------------------------
# Security Agent Endpoints
# ---------------------------------------------------------

@app.post("/security/run", response_model=SecurityRunResponse)
def run_security_agent(request: SecurityRunRequest):
    """
    Run the Security Agent through FastAPI.

    This endpoint:
    - scans the target project folder
    - generates SecurityReport_v1.json
    - generates SecurityReport_v1.md
    - generates SecuritySummaryPack_v1.json
    - generates SecuritySummaryPack_v1.md
    - updates run_metadata.json
    - returns the summary, security gate, and artifact paths
    """

    try:
        result = security_agent.run(
            run_id=request.run_id,
            version=request.version,
            target_path=request.target_path,
            enable_llm=request.enable_llm
        )

        return result

    except FileNotFoundError as error:
        raise HTTPException(
            status_code=404,
            detail=str(error)
        )

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=f"Security Agent failed: {error}"
        )


# ---------------------------------------------------------
# Testing / QA Agent Endpoints
# ---------------------------------------------------------

@app.post("/testing/run", response_model=TestingRunResponse)
def run_testing_agent(request: TestingRunRequest):
    """
    Run the Testing / QA Agent through FastAPI.

    This endpoint:
    - generates pytest files
    - executes generated pytest files
    - generates TestReport_v1.json
    - generates TestReport_v1.md
    - updates run_metadata.json
    - returns the test summary and artifact paths
    """

    try:
        result = tester_agent.run(
            run_id=request.run_id,
            version=request.version,
            target_path=request.target_path
        )

        return result

    except FileNotFoundError as error:
        raise HTTPException(
            status_code=404,
            detail=str(error)
        )

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=f"Testing Agent failed: {error}"
        )