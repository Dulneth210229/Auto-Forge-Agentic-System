import json
import os
from pathlib import Path
from agents.requirement_agent.schemas import IntakeInput, SRS
from agents.requirement_agent.prompt import build_srs_prompt, build_srs_revision_prompt
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
    async def revise_srs(
        self,
        run_id: str,
        current_version: str,
        new_version: str,
        change_request: str
    ) -> dict:
        current_path = (
            self.output_dir
            / "runs"
            / run_id
            / "srs"
            / current_version
            / f"SRS_{current_version}.json"
        )

        if not current_path.exists():
            raise FileNotFoundError(f"Existing SRS not found: {current_path}")

        existing_data = json.loads(current_path.read_text(encoding="utf-8"))
        existing_srs = SRS.model_validate(existing_data)

        prompt = build_srs_revision_prompt(
            existing_srs=existing_srs,
            change_request=change_request,
            new_version=new_version
        )

        llm_output = await self.llm_provider.generate(prompt)

        revised_srs: SRS = parse_srs(llm_output)
        revised_srs.version = new_version

        markdown = render_srs_markdown(revised_srs)

        output_path = self.output_dir / "runs" / run_id / "srs" / new_version
        output_path.mkdir(parents=True, exist_ok=True)

        json_file = output_path / f"SRS_{new_version}.json"
        md_file = output_path / f"SRS_{new_version}.md"

        json_file.write_text(
            json.dumps(revised_srs.model_dump(), indent=2),
            encoding="utf-8"
        )

        md_file.write_text(markdown, encoding="utf-8")

        return {
            "run_id": run_id,
            "previous_version": current_version,
            "new_version": new_version,
            "change_request": change_request,
            "json_path": str(json_file),
            "markdown_path": str(md_file),
            "srs": revised_srs.model_dump()
        }