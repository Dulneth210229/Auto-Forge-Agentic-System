import json
import os
from pathlib import Path
from agents.requirement_agent.schemas import IntakeInput, SRS
from agents.requirement_agent.prompt import build_srs_prompt
from agents.requirement_agent.parser import parse_srs
from agents.requirement_agent.renderer import render_srs_markdown
from tools.llm.provider import LLMProvider


class RequirementAgent:
    def __init__(self, llm_provider: LLMProvider):
        self.llm_provider = llm_provider
        self.output_dir = Path(os.getenv("OUTPUT_DIR", "outputs"))

    def validate_intake(self, intake_data: dict) -> IntakeInput:
        return IntakeInput.model_validate(intake_data)

    def get_clarification_questions(self, intake_data: dict) -> list[str]:
        questions = []

        if not intake_data.get("project_name"):
            questions.append("What is the project name?")

        if not intake_data.get("business_goal"):
            questions.append("What is the main business goal of the E-commerce platform?")

        if not intake_data.get("target_users"):
            questions.append("Who are the target users? Example: customers, admins, sellers.")

        return questions

    async def generate_srs(self, intake_data: dict, run_id: str = "RUN-0001", version: str = "v1") -> dict:
        intake = self.validate_intake(intake_data)

        prompt = build_srs_prompt(intake)
        llm_output = await self.llm_provider.generate(prompt)

        srs: SRS = parse_srs(llm_output)
        srs.version = version

        markdown = render_srs_markdown(srs)

        output_path = self.output_dir / "runs" / run_id / "srs" / version
        output_path.mkdir(parents=True, exist_ok=True)

        json_file = output_path / f"SRS_{version}.json"
        md_file = output_path / f"SRS_{version}.md"

        json_file.write_text(
            json.dumps(srs.model_dump(), indent=2),
            encoding="utf-8"
        )

        md_file.write_text(markdown, encoding="utf-8")

        return {
            "run_id": run_id,
            "version": version,
            "json_path": str(json_file),
            "markdown_path": str(md_file),
            "srs": srs.model_dump()
        }