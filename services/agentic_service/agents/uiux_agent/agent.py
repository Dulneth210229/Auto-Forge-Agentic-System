import asyncio
import inspect
import json
import os
from pathlib import Path

import yaml

from agents.uiux_agent.schemas import UIUXPack, WireframeSpec
from agents.uiux_agent.flow_builder import build_mermaid_from_flow
from agents.uiux_agent.prompt import (
    build_uiux_plan_prompt,
    build_high_fidelity_wireframe_prompt,
)
from agents.uiux_agent.parser import (
    parse_uiux_plan,
    clean_html_output,
)
from agents.uiux_agent.renderer import render_mermaid_to_png, render_html_to_png


class UIUXAgent:
    """
    LLM-only UI/UX Agent for AutoForge.

    Inputs:
    - Approved SRS JSON
    - Approved API contract YAML

    LLM-generated outputs:
    - UI screen inventory
    - User flows
    - Traceability
    - High-fidelity Tailwind HTML wireframes

    Rendered outputs:
    - Mermaid flow PNG
    - Wireframe PNG screenshots

    Important:
    This version does not use hardcoded screen templates.
    """

    def __init__(self, llm_provider=None):
        self.llm_provider = llm_provider
        self.output_dir = Path(os.getenv("OUTPUT_DIR", "outputs"))

    def validate_inputs(self, srs: dict, api_contract: dict) -> dict:
        """
        Validates whether SRS and API contract are enough for UI/UX generation.
        """

        questions = []

        if not srs.get("functional_requirements"):
            questions.append("Approved SRS must contain functional_requirements.")

        if not api_contract.get("paths"):
            questions.append("Approved API contract must contain OpenAPI paths.")

        if not self.llm_provider:
            questions.append("UI/UX Agent requires an LLM provider because templates are disabled.")

        return {
            "valid": len(questions) == 0,
            "clarification_required": len(questions) > 0,
            "questions": questions,
        }

    def load_approved_inputs(
        self,
        run_id: str,
        srs_version: str,
        api_version: str,
    ) -> tuple[dict, dict]:
        """
        Loads approved SRS and approved OpenAPI contract.
        """

        srs_path = (
            self.output_dir
            / "runs"
            / run_id
            / "srs"
            / srs_version
            / f"SRS_{srs_version}.json"
        )

        api_path = (
            self.output_dir
            / "runs"
            / run_id
            / "architecture"
            / api_version
            / f"OpenAPI_{api_version}.yaml"
        )

        if not srs_path.exists():
            raise FileNotFoundError(f"Approved SRS not found: {srs_path}")

        if not api_path.exists():
            raise FileNotFoundError(f"Approved API contract not found: {api_path}")

        srs = json.loads(srs_path.read_text(encoding="utf-8"))
        api_contract = yaml.safe_load(api_path.read_text(encoding="utf-8"))

        return srs, api_contract

    def _run_llm_generate(self, prompt: str) -> str:
        """
        Calls the LLM provider.

        Supports both:
        - async generate()
        - sync generate()
        """

        if not self.llm_provider:
            raise RuntimeError("No LLM provider configured.")

        result = self.llm_provider.generate(prompt)

        if inspect.isawaitable(result):
            return asyncio.run(result)

        return result

    def _generate_uiux_plan_with_llm(
        self,
        project_name: str,
        srs: dict,
        api_contract: dict,
        uiux_version: str,
        change_request: str | None,
    ):
        """
        Uses LLM to generate:
        - screens
        - user flows
        - traceability
        """

        prompt = build_uiux_plan_prompt(
            project_name=project_name,
            srs=srs,
            api_contract=api_contract,
            uiux_version=uiux_version,
            change_request=change_request,
        )

        raw_output = self._run_llm_generate(prompt)

        return parse_uiux_plan(raw_output)

    def _generate_wireframe_html_with_llm(
        self,
        project_name: str,
        screen,
        srs: dict,
        api_contract: dict,
        all_screens: list[dict],
        change_request: str | None,
    ) -> str:
        """
        Uses LLM to generate one high-fidelity HTML wireframe.

        No fallback template is used.
        If the LLM output is invalid, this method raises an error.
        """

        prompt = build_high_fidelity_wireframe_prompt(
            project_name=project_name,
            screen=screen,
            srs=srs,
            api_contract=api_contract,
            all_screens=all_screens,
            change_request=change_request,
        )

        raw_output = self._run_llm_generate(prompt)

        return clean_html_output(raw_output)

    def generate_design_pack(
        self,
        run_id: str,
        srs_version: str = "v1",
        api_version: str = "v1",
        uiux_version: str = "v1",
        include_admin: bool = True,
        render_images: bool = True,
        change_request: str | None = None,
        status: str = "generated",
        previous_version: str | None = None,
        use_llm_wireframes: bool = True,
    ) -> dict:
        """
        Generates a full UI/UX design pack using LLM only.

        The parameter use_llm_wireframes remains for API compatibility,
        but this LLM-only version always requires LLM.
        """

        srs, api_contract = self.load_approved_inputs(
            run_id=run_id,
            srs_version=srs_version,
            api_version=api_version,
        )

        validation = self.validate_inputs(srs, api_contract)
        if not validation["valid"]:
            return validation

        project_name = srs.get("project_name", "AutoForge E-commerce Platform")

        base_dir = self.output_dir / "runs" / run_id / "uiux" / uiux_version
        flows_dir = base_dir / "flows"
        wireframes_dir = base_dir / "wireframes"

        flows_dir.mkdir(parents=True, exist_ok=True)
        wireframes_dir.mkdir(parents=True, exist_ok=True)

        # ---------------------------------------------------------
        # 1. LLM generates screen inventory + user flow + traceability
        # ---------------------------------------------------------
        screens, user_flows, traceability = self._generate_uiux_plan_with_llm(
            project_name=project_name,
            srs=srs,
            api_contract=api_contract,
            uiux_version=uiux_version,
            change_request=change_request,
        )

        primary_flow = user_flows[0]
        mermaid = build_mermaid_from_flow(primary_flow)

        flow_json_path = flows_dir / f"user_flows_{uiux_version}.json"
        flow_mmd_path = flows_dir / f"user_flows_{uiux_version}.mmd"

        flow_json_path.write_text(
            json.dumps(primary_flow.model_dump(), indent=2),
            encoding="utf-8",
        )

        flow_mmd_path.write_text(mermaid, encoding="utf-8")

        flow_png_path = None
        if render_images:
            flow_png_path = render_mermaid_to_png(flow_mmd_path)

        # ---------------------------------------------------------
        # 2. LLM generates high-fidelity HTML for every screen
        # ---------------------------------------------------------
        wireframe_html_paths = []
        wireframe_png_paths = []

        all_screens_data = [screen.model_dump() for screen in screens]

        for screen in screens:
            html_path = wireframes_dir / screen.file_name

            html = self._generate_wireframe_html_with_llm(
                project_name=project_name,
                screen=screen,
                srs=srs,
                api_contract=api_contract,
                all_screens=all_screens_data,
                change_request=change_request,
            )

            html_path.write_text(html, encoding="utf-8")
            wireframe_html_paths.append(str(html_path))

            if render_images:
                png_path = html_path.with_suffix(".png")
                rendered = render_html_to_png(html_path, png_path)

                if rendered:
                    wireframe_png_paths.append(rendered)

        # ---------------------------------------------------------
        # 3. Save machine-readable wireframe spec
        # ---------------------------------------------------------
        wireframe_spec = WireframeSpec(
            version=uiux_version,
            screens=screens,
        )

        wireframes_json_path = wireframes_dir / f"wireframes_{uiux_version}.json"
        wireframes_json_path.write_text(
            json.dumps(wireframe_spec.model_dump(), indent=2),
            encoding="utf-8",
        )

        # ---------------------------------------------------------
        # 4. Save traceability
        # ---------------------------------------------------------
        trace_path = base_dir / f"trace_uiux_{uiux_version}.json"
        trace_path.write_text(
            json.dumps([link.model_dump() for link in traceability], indent=2),
            encoding="utf-8",
        )

        # ---------------------------------------------------------
        # 5. Save UIUXPack
        # ---------------------------------------------------------
        uiux_pack = UIUXPack(
            project_name=project_name,
            version=uiux_version,
            source_srs_version=srs_version,
            source_api_version=api_version,
            status=status,
            screens=screens,
            user_flows=user_flows,
            traceability=traceability,
            flow_mmd_path=str(flow_mmd_path),
            flow_png_path=flow_png_path,
            wireframe_html_paths=wireframe_html_paths,
            wireframe_png_paths=wireframe_png_paths,
        )

        pack_json_path = base_dir / f"UIUXPack_{uiux_version}.json"
        pack_md_path = base_dir / f"UIUXPack_{uiux_version}.md"

        pack_json_path.write_text(
            json.dumps(uiux_pack.model_dump(), indent=2),
            encoding="utf-8",
        )

        pack_md_path.write_text(
            self._render_markdown_summary(
                pack=uiux_pack,
                change_request=change_request,
                previous_version=previous_version,
            ),
            encoding="utf-8",
        )

        revision_log_path = None

        if change_request:
            revision_log_path = base_dir / f"revision_note_{uiux_version}.txt"
            revision_log_path.write_text(
                f"Previous version: {previous_version or 'N/A'}\n"
                f"New version: {uiux_version}\n"
                f"Change request: {change_request}\n"
                f"Generation mode: LLM-only high-fidelity UI/UX generation\n",
                encoding="utf-8",
            )

        return {
            "run_id": run_id,
            "uiux_version": uiux_version,
            "previous_version": previous_version,
            "change_request": change_request,
            "generation_mode": "llm_only_high_fidelity",
            "updated_artifacts": [
                "llm_generated_screens",
                "llm_generated_user_flows",
                "llm_generated_traceability",
                "llm_generated_high_fidelity_wireframes",
                "wireframe_pngs",
                "flow_png",
                "uiux_pack",
            ],
            "uiux_pack_path": str(pack_json_path),
            "markdown_path": str(pack_md_path),
            "flow_json_path": str(flow_json_path),
            "flow_mmd_path": str(flow_mmd_path),
            "flow_png_path": flow_png_path,
            "wireframes_json_path": str(wireframes_json_path),
            "wireframe_html_paths": wireframe_html_paths,
            "wireframe_png_paths": wireframe_png_paths,
            "traceability_path": str(trace_path),
            "revision_note_path": str(revision_log_path) if revision_log_path else None,
        }

    def revise_design_pack(
        self,
        run_id: str,
        current_version: str,
        new_version: str,
        change_request: str,
        srs_version: str = "v1",
        api_version: str = "v1",
        include_admin: bool = True,
        render_images: bool = True,
        use_llm_wireframes: bool = True,
    ) -> dict:
        """
        Revises UI/UX output as a new LLM-only version.
        """

        current_pack_path = (
            self.output_dir
            / "runs"
            / run_id
            / "uiux"
            / current_version
            / f"UIUXPack_{current_version}.json"
        )

        if not current_pack_path.exists():
            raise FileNotFoundError(f"Current UIUXPack not found: {current_pack_path}")

        return self.generate_design_pack(
            run_id=run_id,
            srs_version=srs_version,
            api_version=api_version,
            uiux_version=new_version,
            include_admin=include_admin,
            render_images=render_images,
            change_request=change_request,
            status="revised",
            previous_version=current_version,
            use_llm_wireframes=True,
        )

    def _render_markdown_summary(
        self,
        pack: UIUXPack,
        change_request: str | None = None,
        previous_version: str | None = None,
    ) -> str:
        """
        Human-readable Markdown summary.
        """

        lines = [
            f"# UI/UX Design Pack: {pack.project_name}",
            "",
            f"**Version:** {pack.version}",
            f"**Status:** {pack.status}",
            f"**Generation Mode:** LLM-only high-fidelity UI/UX generation",
            f"**Source SRS:** {pack.source_srs_version}",
            f"**Source API Contract:** {pack.source_api_version}",
        ]

        if previous_version:
            lines.append(f"**Previous Version:** {previous_version}")

        if change_request:
            lines.extend([
                "",
                "## Revision Request",
                change_request,
            ])

        lines.extend([
            "",
            "## Screens",
        ])

        for screen in pack.screens:
            lines.append(f"- **{screen.id} — {screen.name}**: {screen.description}")

        lines.append("")
        lines.append("## User Flows")

        for flow in pack.user_flows:
            lines.append(f"- **{flow.id} — {flow.name}** ({flow.actor})")

        lines.append("")
        lines.append("## Traceability")

        for link in pack.traceability:
            lines.append(f"- {link.requirement_id} → {link.screen_id} ({link.screen_name})")

        return "\n".join(lines)