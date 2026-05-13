import logging
import threading
import zipfile
import tempfile
from datetime import datetime
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import PlainTextResponse, FileResponse
from pydantic import BaseModel, Field

from agents.requirement_agent.agent import RequirementAgent
from agents.domain_agent.agent import DomainAgent
from agents.architect_agent.agent import ArchitectAgent
from agents.uiux_agent.agent import UIUXAgent
from agents.coder_agent.agent import CoderAgent
from agents.security_agent.agent import SecurityAgent
from agents.tester_agent.agent import TesterAgent
from tools.llm.provider import OllamaProvider


logger = logging.getLogger(__name__)


app = FastAPI(
    title="AutoForge Agentic Service API",
    description="Single-service multi-agent system for E-commerce SDLC automation.",
    version="1.0.0",
)


# ---------------------------------------------------------
# CORS Middleware
# Allows React frontend requests from Vite dev server.
# ---------------------------------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------------------------------------------------
# Agent instances
# ---------------------------------------------------------
requirement_agent = RequirementAgent(llm_provider=OllamaProvider())
domain_agent = DomainAgent(llm_provider=OllamaProvider())
architect_agent = ArchitectAgent()
uiux_agent = UIUXAgent(llm_provider=OllamaProvider())
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
        description="AutoForge run ID",
    )

    version: str = Field(
        default="v1",
        description="Artifact version",
    )

    target_path: str = Field(
        default="./sample_ecommerce_app",
        description="Target source code folder to scan",
    )

    enable_llm: bool = Field(
        default=False,
        description="Enable Ollama LLM-assisted secure code review",
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
        description="AutoForge run ID",
    )

    version: str = Field(
        default="v1",
        description="Artifact version",
    )

    target_path: str = Field(
        default="./sample_ecommerce_app",
        description="Target source code folder to test",
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

    Inputs from multiple agents:
    - srs_version: SRS from Requirement Agent
    - architecture_version: OpenAPI, SDS, DBPack from Architect Agent
    - domain_version: DomainPack from Domain Agent
    - uiux_version: UI/UX output version
    """

    run_id: str = Field(
        default="RUN-0001",
        description="AutoForge run ID",
    )

    srs_version: str = Field(
        default="v1",
        description="Source SRS version from Requirement Agent",
    )

    code_version: str = Field(
        default="v1",
        description="Target code version to generate",
    )

    domain_version: str = Field(
        default="v1",
        description="DomainPack version from Domain Agent",
    )

    architecture_version: str = Field(
        default="v1",
        description="Architecture version from Architect Agent",
    )

    uiux_version: str = Field(
        default="v1",
        description="UI/UX version containing user flows and wireframes",
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

    input_artifacts: dict = Field(
        default_factory=dict,
        description="Artifact files used by the Coder Agent",
    )

    validation_warnings: list[str] = Field(
        default_factory=list,
        description="Warnings about OpenAPI or DBPack coverage",
    )


class CoderReviseRequest(BaseModel):
    """
    Request body for revising generated code.

    This creates a new code version from an existing generated code version.
    """

    run_id: str = Field(
        default="RUN-0001",
        description="AutoForge run ID",
    )

    current_code_version: str = Field(
        default="v1",
        description="Existing code version to revise",
    )

    new_code_version: str = Field(
        default="v2",
        description="New code version to create",
    )

    srs_version: str = Field(
        default="v1",
        description="SRS version used as source context",
    )

    domain_version: str = Field(
        default="v1",
        description="DomainPack version used as source context",
    )

    architecture_version: str = Field(
        default="v1",
        description="Architecture version used as source context",
    )

    uiux_version: str = Field(
        default="v1",
        description="UI/UX version containing user flows and wireframes",
    )

    change_request: str = Field(
        ...,
        description="Human revision instruction for the generated code",
    )


# ---------------------------------------------------------
# Shared Safe Artifact Path Resolver
# ---------------------------------------------------------
def resolve_safe_artifact_path(path: str) -> Path:
    """
    Safely resolves generated artifact paths.

    Only allows access to files/folders inside:
    - outputs/
    - artifacts/

    This prevents users from downloading or reading system files.
    """

    requested_path = Path(path)

    if not requested_path.is_absolute():
        requested_path = Path.cwd() / requested_path

    requested_path = requested_path.resolve()
    project_root = Path.cwd().resolve()

    allowed_roots = [
        (project_root / "outputs").resolve(),
        (project_root / "artifacts").resolve(),
    ]

    is_allowed = False

    for root in allowed_roots:
        try:
            requested_path.relative_to(root)
            is_allowed = True
            break
        except ValueError:
            pass

    if not is_allowed:
        raise HTTPException(
            status_code=403,
            detail="Only files or folders inside outputs/ or artifacts/ can be accessed.",
        )

    if not requested_path.exists():
        raise HTTPException(
            status_code=404,
            detail=f"Path not found: {path}",
        )

    return requested_path


# ---------------------------------------------------------
# Health Endpoint
# ---------------------------------------------------------
@app.get("/health")
def health():
    return {
        "status": "ok",
        "service": "autoforge-agentic-service",
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
            "questions": questions,
        }

    intake = requirement_agent.validate_intake(payload)

    return {
        "valid": True,
        "clarification_required": False,
        "intake": intake.model_dump(),
    }


@app.post("/requirements/srs/generate")
async def generate_srs(payload: dict):
    run_id = payload.get("run_id", "RUN-0001")
    version = payload.get("version", "v1")
    intake = payload.get("intake", payload)

    result = await requirement_agent.generate_srs(
        intake_data=intake,
        run_id=run_id,
        version=version,
    )

    return result


@app.post("/requirements/srs/revise")
async def revise_srs(payload: dict):
    result = await requirement_agent.revise_srs(
        run_id=payload["run_id"],
        current_version=payload["current_version"],
        new_version=payload["new_version"],
        change_request=payload["change_request"],
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
            "knowledge/ecommerce_domain_knowledge.txt",
        ),
        vector_store_type=payload.get("vector_store_type", "faiss"),
    )

    return result


@app.post("/domain/pack/generate")
async def generate_domain_pack(payload: dict):
    result = await domain_agent.generate_domain_pack(
        run_id=payload.get("run_id", "RUN-0001"),
        srs_version=payload.get("srs_version", "v1"),
        domain_version=payload.get("domain_version", "v1"),
        vector_store_type=payload.get("vector_store_type", "faiss"),
        top_k=payload.get("top_k", 6),
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

    Generates:
    - SDS JSON/Markdown
    - OpenAPI YAML
    - DBPack
    - UML/diagram source files
    - UML/diagram images or HTML if export_visuals=True
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
            detail=str(error),
        )

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=f"Architect Agent failed: {error}",
        )


@app.post("/architecture/revise")
def revise_architecture(payload: dict):
    """
    Revises an existing architecture output version using user feedback.
    """

    try:
        result = architect_agent.revise_architecture(
            run_id=payload["run_id"],
            current_version=payload["current_version"],
            new_version=payload["new_version"],
            change_request=payload["change_request"],
            export_visuals=payload.get("export_visuals", True),
        )

        return result

    except FileNotFoundError as error:
        raise HTTPException(
            status_code=404,
            detail=str(error),
        )

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=f"Architect Agent revision failed: {error}",
        )


@app.get("/architecture/download-pack")
def download_architecture_pack(
    run_id: str = "RUN-0001",
    architecture_version: str = "v1",
):
    """
    Downloads all Architect Agent outputs as a ZIP file.

    Includes:
    - SDS JSON
    - SDS Markdown
    - OpenAPI YAML
    - DBPack JSON
    - UML images
    - HTML diagrams/reports
    - Mermaid/PlantUML source files
    """

    project_root = Path.cwd().resolve()

    architecture_dir = (
        project_root
        / "outputs"
        / "runs"
        / run_id
        / "architecture"
        / architecture_version
    ).resolve()

    if not architecture_dir.exists():
        raise HTTPException(
            status_code=404,
            detail=f"Architecture folder not found: {architecture_dir}",
        )

    exports_dir = (
        project_root
        / "outputs"
        / "runs"
        / run_id
        / "exports"
    ).resolve()

    exports_dir.mkdir(parents=True, exist_ok=True)

    zip_file_path = exports_dir / f"ArchitecturePack_{architecture_version}.zip"

    if zip_file_path.exists():
        zip_file_path.unlink()

    blocked_folders = {
        "__pycache__",
        ".pytest_cache",
        ".git",
        "node_modules",
        "dist",
        "build",
        ".venv",
        "venv",
    }

    with zipfile.ZipFile(zip_file_path, "w", zipfile.ZIP_DEFLATED) as zip_file:
        for file_path in architecture_dir.rglob("*"):
            if not file_path.is_file():
                continue

            if any(part in blocked_folders for part in file_path.parts):
                continue

            zip_file.write(
                file_path,
                arcname=file_path.relative_to(architecture_dir),
            )

    return FileResponse(
        path=zip_file_path,
        media_type="application/zip",
        filename=f"ArchitecturePack_{run_id}_{architecture_version}.zip",
    )


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
# Coder Agent Endpoints
# ---------------------------------------------------------
@app.post("/coder/generate", response_model=CoderGenerateResponse)
async def generate_code(request: CoderGenerateRequest):
    """
    Generate runnable application code from multiple approved artifacts using the Coder Agent.

    Inputs:
    - SRS from Requirement Agent
    - OpenAPI, SDS, DBPack from Architect Agent
    - DomainPack from Domain Agent
    - UI/UX outputs from UI/UX Agent
    """

    try:
        logger.info(
            "Coder Agent: Generating code for "
            f"run_id={request.run_id}, "
            f"srs_version={request.srs_version}, "
            f"code_version={request.code_version}, "
            f"architecture_version={request.architecture_version}, "
            f"domain_version={request.domain_version}"
        )

        result = await coder_agent.generate_code(
            run_id=request.run_id,
            srs_version=request.srs_version,
            code_version=request.code_version,
            domain_version=request.domain_version,
            architecture_version=request.architecture_version,
            uiux_version=request.uiux_version,
        )

        logger.info(
            f"Coder Agent: Successfully generated {result.get('generated_file_count', 0)} files"
        )

        return result

    except FileNotFoundError as error:
        logger.error(f"Coder Agent: Required artifact file not found - {error}")
        raise HTTPException(
            status_code=404,
            detail=f"Required artifact not found: {error}",
        )

    except Exception as error:
        logger.error(
            f"Coder Agent: Unexpected error - {type(error).__name__}: {error}",
            exc_info=True,
        )
        raise HTTPException(
            status_code=500,
            detail=f"Coder Agent failed: {type(error).__name__}: {error}",
        )


@app.post("/coder/revise")
async def revise_code(request: CoderReviseRequest):
    """
    Revise an existing generated code version.

    Example:
    v5 generated app + user change request -> v6 generated app.
    """

    try:
        logger.info(
            f"Coder Agent: Revising code for run_id={request.run_id}, "
            f"current_code_version={request.current_code_version}, "
            f"new_code_version={request.new_code_version}"
        )

        result = await coder_agent.revise_code(
            run_id=request.run_id,
            current_code_version=request.current_code_version,
            new_code_version=request.new_code_version,
            change_request=request.change_request,
            srs_version=request.srs_version,
            domain_version=request.domain_version,
            architecture_version=request.architecture_version,
            uiux_version=request.uiux_version,
        )

        logger.info(
            f"Coder Agent: Revision completed. "
            f"Changed files: {result.get('changed_file_count', 0)}"
        )

        return result

    except FileNotFoundError as error:
        logger.error(f"Coder Agent revision: File not found - {error}")
        raise HTTPException(
            status_code=404,
            detail=f"Required file not found: {error}",
        )

    except Exception as error:
        logger.error(
            f"Coder Agent revision failed - {type(error).__name__}: {error}",
            exc_info=True,
        )
        raise HTTPException(
            status_code=500,
            detail=f"Coder Agent revision failed: {type(error).__name__}: {error}",
        )


# ---------------------------------------------------------
# Security Agent Endpoints
# ---------------------------------------------------------
@app.post("/security/run", response_model=SecurityRunResponse)
def run_security_agent(request: SecurityRunRequest):
    """
    Run the Security Agent through FastAPI.

    This endpoint:
    - scans the target project folder
    - generates SecurityReport_vX.json
    - generates SecurityReport_vX.md
    - generates SecuritySummaryPack_vX.json
    - generates SecuritySummaryPack_vX.md
    - updates run_metadata.json
    - returns the summary, security gate, and artifact paths
    """

    try:
        result = security_agent.run(
            run_id=request.run_id,
            version=request.version,
            target_path=request.target_path,
            enable_llm=request.enable_llm,
        )

        return result

    except FileNotFoundError as error:
        raise HTTPException(
            status_code=404,
            detail=str(error),
        )

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=f"Security Agent failed: {error}",
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
    - generates TestReport_vX.json
    - generates TestReport_vX.md
    - updates run_metadata.json
    - returns the test summary and artifact paths
    """

    try:
        result = tester_agent.run(
            run_id=request.run_id,
            version=request.version,
            target_path=request.target_path,
        )

        return result

    except FileNotFoundError as error:
        raise HTTPException(
            status_code=404,
            detail=str(error),
        )

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=f"Testing Agent failed: {error}",
        )


# ---------------------------------------------------------
# Artifact Preview / Tree / Download Endpoints
# ---------------------------------------------------------
@app.get("/artifacts/read", response_class=PlainTextResponse)
def read_generated_artifact(path: str):
    """
    Reads text-based generated artifact files for frontend preview.

    Used for:
    - Markdown reports
    - JSON files
    - YAML files
    - Mermaid source
    - PlantUML source
    - HTML source code
    - generated code files
    """

    requested_path = resolve_safe_artifact_path(path)

    if not requested_path.is_file():
        raise HTTPException(
            status_code=400,
            detail="The provided path must be a file.",
        )

    allowed_extensions = [
        ".json",
        ".md",
        ".txt",
        ".yaml",
        ".yml",
        ".mmd",
        ".puml",
        ".html",
        ".css",
        ".js",
        ".jsx",
        ".ts",
        ".tsx",
        ".py",
        ".log",
        ".sh",
    ]

    allowed_names = [
        "Dockerfile",
        ".gitignore",
        ".dockerignore",
    ]

    if (
        requested_path.suffix.lower() not in allowed_extensions
        and requested_path.name not in allowed_names
    ):
        raise HTTPException(
            status_code=400,
            detail="Only text-based generated artifact files can be previewed.",
        )

    return requested_path.read_text(encoding="utf-8", errors="ignore")


@app.get("/artifacts/file")
def serve_generated_artifact_file(path: str):
    """
    Serves visual/browser-renderable generated files.

    Used by the frontend to display:
    - UML PNG diagrams
    - SVG diagrams
    - JPG/JPEG diagrams
    - HTML diagram/report previews inside iframe
    - PDF files if needed
    """

    requested_path = resolve_safe_artifact_path(path)

    if not requested_path.is_file():
        raise HTTPException(
            status_code=400,
            detail="The provided path must be a file.",
        )

    allowed_extensions = [
        ".png",
        ".jpg",
        ".jpeg",
        ".svg",
        ".webp",
        ".html",
        ".pdf",
    ]

    if requested_path.suffix.lower() not in allowed_extensions:
        raise HTTPException(
            status_code=400,
            detail="Only visual/browser-renderable artifact files can be served.",
        )

    return FileResponse(path=requested_path)


@app.get("/artifacts/tree")
def get_artifact_tree(path: str):
    """
    Returns the exact folder/file tree for a generated artifact folder.
    """

    root_path = resolve_safe_artifact_path(path)

    if not root_path.is_dir():
        raise HTTPException(
            status_code=400,
            detail="The provided path must be a folder.",
        )

    blocked_folders = {
        "__pycache__",
        ".pytest_cache",
        ".git",
        "node_modules",
        "dist",
        "build",
        ".venv",
        "venv",
    }

    def build_tree(current_path: Path):
        children = []

        for child in sorted(
            current_path.iterdir(),
            key=lambda item: (item.is_file(), item.name.lower()),
        ):
            if child.name in blocked_folders:
                continue

            item = {
                "name": child.name,
                "path": str(child),
                "type": "folder" if child.is_dir() else "file",
            }

            if child.is_file():
                item["size"] = child.stat().st_size

            if child.is_dir():
                item["children"] = build_tree(child)

            children.append(item)

        return children

    return {
        "root_name": root_path.name,
        "root_path": str(root_path),
        "tree": build_tree(root_path),
    }


@app.get("/artifacts/download-folder")
def download_artifact_folder(path: str):
    """
    Downloads a generated artifact folder as a ZIP file.
    """

    folder_path = resolve_safe_artifact_path(path)

    if not folder_path.is_dir():
        raise HTTPException(
            status_code=400,
            detail="The provided path must be a folder.",
        )

    blocked_folders = {
        "__pycache__",
        ".pytest_cache",
        ".git",
        "node_modules",
        "dist",
        "build",
        ".venv",
        "venv",
    }

    zip_file_path = Path(tempfile.gettempdir()) / f"{folder_path.name}.zip"

    if zip_file_path.exists():
        zip_file_path.unlink()

    with zipfile.ZipFile(zip_file_path, "w", zipfile.ZIP_DEFLATED) as zip_file:
        for file_path in folder_path.rglob("*"):
            if not file_path.is_file():
                continue

            if any(part in blocked_folders for part in file_path.parts):
                continue

            arcname = file_path.relative_to(folder_path.parent)
            zip_file.write(file_path, arcname)

    return FileResponse(
        path=zip_file_path,
        filename=f"{folder_path.name}.zip",
        media_type="application/zip",
    )