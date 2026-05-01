from fastapi import FastAPI
from agents.requirement_agent.agent import RequirementAgent
from agents.coder_agent.agent import CoderAgent
from tools.llm.provider import OllamaProvider

app = FastAPI(
    title="AutoForge Requirement Agent API",
    version="1.0.0"
)

requirement_agent = RequirementAgent(llm_provider=OllamaProvider())
coder_agent = CoderAgent()


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

@app.post("/coder/generate")
def generate_code(payload: dict):
    result = coder_agent.generate_code(
        run_id=payload.get("run_id", "RUN-0001"),
        srs_version=payload.get("srs_version", "v1"),
        code_version=payload.get("code_version", "v1")
    )
    return result