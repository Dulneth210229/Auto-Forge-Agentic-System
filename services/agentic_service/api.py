import logging
from typing import Optional

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
    
    Inputs from multiple agents:
    - srs_version: SRS from Requirement Agent
    - architecture_version: OpenAPI, SDS from Architect Agent
    - domain_version: DomainPack from Domain Agent
    - Database artifacts are loaded from architecture_version path
    """

    run_id: str = Field(
        default="RUN-0001",
        description="AutoForge run ID"
    )

    srs_version: str = Field(
        default="v1",
        description="Source SRS version from Requirement Agent (e.g., v1, v2)"
    )

    code_version: str = Field(
        default="v1",
        description="Target code version to generate (e.g., v1, v2)"
    )

    domain_version: str = Field(
        default="v1",
        description="DomainPack version from Domain Agent (e.g., v1, v2)"
    )

    architecture_version: str = Field(
        default="v1",
        description="Architecture version (OpenAPI, SDS, DBPack from Architect Agent)"
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
        description="Artifact files used by the Coder Agent"
    )

    validation_warnings: list[str] = Field(
        default_factory=list,
        description="Warnings about OpenAPI or DBPack coverage"
    )


class CoderReviseRequest(BaseModel):
    """
    Request body for revising generated code.

    This creates a new code version from an existing generated code version.
    """

    run_id: str = Field(
        default="RUN-0001",
        description="AutoForge run ID"
    )

    current_code_version: str = Field(
        default="v1",
        description="Existing code version to revise"
    )

    new_code_version: str = Field(
        default="v2",
        description="New code version to create"
    )

    srs_version: str = Field(
        default="v1",
        description="SRS version used as source context"
    )

    domain_version: str = Field(
        default="v1",
        description="DomainPack version used as source context"
    )

    architecture_version: str = Field(
        default="v1",
        description="Architecture version used as source context"
    )

    change_request: str = Field(
        ...,
        description="Human revision instruction for the generated code"
    )

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

@app.post("/uiux/srs/validate")
def validate_uiux_inputs(payload: dict):
    try:
        srs, domain_pack, sds, api_contract, db_pack = uiux_agent.load_approved_inputs(
            run_id=payload.get("run_id", "RUN-0001"),
            srs_version=payload.get("srs_version", "v1"),
            domain_version=payload.get("domain_version", "v1"),
            architecture_version=payload.get("architecture_version", "v1"),
        )

        return uiux_agent.validate_inputs(
            srs=srs,
            domain_pack=domain_pack,
            sds=sds,
            api_contract=api_contract,
            db_pack=db_pack,
        )

    except Exception as error:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"{type(error).__name__}: {str(error)}")


@app.post("/uiux/designpack/generate")
def generate_uiux_design_pack(payload: dict):
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
        )

    except Exception as error:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"{type(error).__name__}: {str(error)}")


@app.post("/uiux/designpack/revise")
def revise_uiux_design_pack(payload: dict):
    try:
        if not payload.get("change_request"):
            raise HTTPException(
                status_code=400,
                detail="change_request is required when revising UI/UX outputs."
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
        )

    except HTTPException:
        raise

    except Exception as error:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"{type(error).__name__}: {str(error)}")


# ---------------------------------------------------------
# Coder Agent Endpoints
# ---------------------------------------------------------

@app.post("/coder/generate", response_model=CoderGenerateResponse)
async def generate_code(request: CoderGenerateRequest):
    """
    Generate runnable application code from multiple approved artifacts using the Coder Agent.

    Inputs:
    - SRS from Requirement Agent (srs_version)
    - OpenAPI.yaml, SDS from Architect Agent (architecture_version)
    - DBPack from Database Agent (architecture_version)
    - DomainPack from Domain Agent (domain_version)

    This endpoint:
    - reads SRS_{srs_version}.json
    - reads OpenAPI.yaml and SDS.json from architecture
    - reads DBPack.json from database
    - reads DomainPack.json from domain
    - generates code files based on all inputs (backend, frontend, devops)
    - creates CodeManifest_{code_version}.json
    - returns generated file paths and count
    """
    
    try:
        logger.info(f"Coder Agent: Generating code for run_id={request.run_id}, srs_version={request.srs_version}, code_version={request.code_version}, architecture_version={request.architecture_version}, domain_version={request.domain_version}")
        
        result = await coder_agent.generate_code(
            run_id=request.run_id,
            srs_version=request.srs_version,
            code_version=request.code_version,
            domain_version=request.domain_version,
            architecture_version=request.architecture_version
        )
        
        logger.info(f"Coder Agent: Successfully generated {result.get('generated_file_count', 0)} files")
        return result
    
    except FileNotFoundError as error:
        logger.error(f"Coder Agent: Required artifact file not found - {error}")
        raise HTTPException(
            status_code=404,
            detail=f"Required artifact not found: {error}"
        )
    
    except Exception as error:
        logger.error(f"Coder Agent: Unexpected error - {type(error).__name__}: {error}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Coder Agent failed: {type(error).__name__}: {error}"
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
            detail=f"Required file not found: {error}"
        )

    except Exception as error:
        logger.error(
            f"Coder Agent revision failed - {type(error).__name__}: {error}",
            exc_info=True,
        )
        raise HTTPException(
            status_code=500,
            detail=f"Coder Agent revision failed: {type(error).__name__}: {error}"
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