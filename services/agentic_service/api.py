from fastapi import FastAPI
from agents.requirement_agent.agent import RequirementAgent
from tools.llm.provider import OllamaProvider
from agents.domain_agent.agent import DomainAgent

app = FastAPI(
    title="AutoForge Agentic Service API",
    description="Single-service multi-agent system for E-commerce SDLC automation.",
    version="1.0.0"
)

requirement_agent = RequirementAgent(llm_provider=OllamaProvider())
domain_agent = DomainAgent(llm_provider=OllamaProvider())

@app.get("/health")
def health():
    return {
        "status": "ok",
        "service": "autoforge-requirement-agent"
    }


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


@app.post("/domain/knowledge/ingest")
def ingest_domain_knowledge(payload: dict):
    result = domain_agent.ingest_domain_knowledge(
        file_path=payload.get("file_path", "knowledge/ecommerce_domain_knowledge.txt"),
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