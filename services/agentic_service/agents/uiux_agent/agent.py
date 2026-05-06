# import asyncio
# import inspect
# import json
# import os
# from pathlib import Path

# import yaml

# from agents.uiux_agent.schemas import UIUXPack, WireframeSpec
# from agents.uiux_agent.flow_builder import build_mermaid_from_flow
# from agents.uiux_agent.prompt import (
#     build_uiux_plan_prompt,
#     build_uiux_plan_repair_prompt,
#     build_high_fidelity_wireframe_prompt,
#     build_wireframe_repair_prompt,
#     build_final_html_regeneration_prompt,

# )
# from agents.uiux_agent.parser import (
#     parse_uiux_plan,
#     clean_html_output,
#     UIUXParseError,
#     WireframeParseError,
# )
# from agents.uiux_agent.renderer import render_mermaid_to_png, render_html_to_png


# class UIUXAgent:
#     """
#     LLM-only UI/UX Agent.

#     Inputs:
#     - Approved SRS
#     - Approved DomainPack
#     - Approved Architecture output excluding diagrams:
#       SDS JSON, OpenAPI YAML, DBPack JSON

#     Outputs:
#     - LLM-generated screens
#     - LLM-generated user flows
#     - LLM-generated traceability
#     - LLM-generated high-fidelity HTML wireframes
#     - PNG screenshots
#     """

#     def __init__(self, llm_provider=None):
#         self.llm_provider = llm_provider
#         self.output_dir = Path(os.getenv("OUTPUT_DIR", "outputs"))

#     def _run_llm_generate(self, prompt: str, json_mode: bool = False) -> str:
#         """
#         Supports provider.generate(prompt) and provider.generate(prompt, json_mode=True).
#         """

#         if not self.llm_provider:
#             raise RuntimeError("UI/UX Agent requires an LLM provider.")

#         try:
#             result = self.llm_provider.generate(prompt, json_mode=json_mode)
#         except TypeError:
#             result = self.llm_provider.generate(prompt)

#         if inspect.isawaitable(result):
#             return asyncio.run(result)

#         return result

#     def _find_file(self, folder: Path, preferred_name: str, fallback_patterns: list[str]) -> Path:
#         """
#         Finds a required artifact even if the exact file name is slightly different.
#         """

#         preferred = folder / preferred_name
#         if preferred.exists():
#             return preferred

#         for pattern in fallback_patterns:
#             matches = list(folder.glob(pattern))
#             if matches:
#                 return matches[0]

#         raise FileNotFoundError(
#             f"Could not find {preferred_name} in {folder}. Tried patterns: {fallback_patterns}"
#         )

#     def load_approved_inputs(
#         self,
#         run_id: str,
#         srs_version: str,
#         domain_version: str,
#         architecture_version: str,
#     ) -> tuple[dict, dict, dict, dict, dict]:
#         """
#         Loads approved upstream artifacts.
#         Architecture diagrams are not loaded.
#         """

#         run_dir = self.output_dir / "runs" / run_id

#         srs_dir = run_dir / "srs" / srs_version
#         domain_dir = run_dir / "domain" / domain_version
#         architecture_dir = run_dir / "architecture" / architecture_version

#         srs_path = self._find_file(
#             srs_dir,
#             f"SRS_{srs_version}.json",
#             ["SRS_*.json", "*.json"],
#         )

#         domain_path = self._find_file(
#             domain_dir,
#             f"DomainPack_{domain_version}.json",
#             ["DomainPack_*.json", "*.json"],
#         )

#         sds_path = self._find_file(
#             architecture_dir,
#             f"SDS_{architecture_version}.json",
#             ["SDS_*.json", "*SDS*.json", "*.json"],
#         )

#         openapi_path = self._find_file(
#             architecture_dir,
#             f"OpenAPI_{architecture_version}.yaml",
#             ["OpenAPI_*.yaml", "*openapi*.yaml", "*.yaml", "*.yml"],
#         )

#         db_pack_path = self._find_file(
#             architecture_dir,
#             f"DBPack_{architecture_version}.json",
#             ["DBPack_*.json", "*DB*.json", "*db*.json"],
#         )

#         srs = json.loads(srs_path.read_text(encoding="utf-8"))
#         domain_pack = json.loads(domain_path.read_text(encoding="utf-8"))
#         sds = json.loads(sds_path.read_text(encoding="utf-8"))
#         api_contract = yaml.safe_load(openapi_path.read_text(encoding="utf-8"))
#         db_pack = json.loads(db_pack_path.read_text(encoding="utf-8"))

#         return srs, domain_pack, sds, api_contract, db_pack

#     def validate_inputs(
#         self,
#         srs: dict,
#         domain_pack: dict,
#         sds: dict,
#         api_contract: dict,
#         db_pack: dict,
#     ) -> dict:
#         questions = []

#         if not srs.get("functional_requirements"):
#             questions.append("Approved SRS must contain functional_requirements.")

#         if not isinstance(api_contract, dict) or not api_contract.get("paths"):
#             questions.append("Approved OpenAPI contract must contain paths.")

#         if not sds:
#             questions.append("Approved SDS is missing or empty.")

#         if not domain_pack:
#             questions.append("Approved DomainPack is missing or empty.")

#         if not db_pack:
#             questions.append("Approved DBPack is missing or empty.")

#         if not self.llm_provider:
#             questions.append("LLM provider is required for UI/UX generation.")

#         return {
#             "valid": len(questions) == 0,
#             "clarification_required": len(questions) > 0,
#             "questions": questions,
#         }

#     def _generate_uiux_plan_with_llm(
#         self,
#         project_name: str,
#         srs: dict,
#         domain_pack: dict,
#         sds: dict,
#         api_contract: dict,
#         db_pack: dict,
#         uiux_version: str,
#         user_prompt: str | None,
#     ):
#         prompt = build_uiux_plan_prompt(
#             project_name=project_name,
#             srs=srs,
#             domain_pack=domain_pack,
#             sds=sds,
#             api_contract=api_contract,
#             db_pack=db_pack,
#             uiux_version=uiux_version,
#             user_prompt=user_prompt,
#         )

#         debug_dir = self.output_dir / "debug" / "uiux"
#         debug_dir.mkdir(parents=True, exist_ok=True)

#         raw_output = self._run_llm_generate(prompt, json_mode=True)
#         (debug_dir / f"{uiux_version}_uiux_plan_raw.json.txt").write_text(
#             raw_output,
#             encoding="utf-8",
#         )

#         try:
#             return parse_uiux_plan(raw_output)

#         except UIUXParseError as first_error:
#             repair_prompt = build_uiux_plan_repair_prompt(
#                 invalid_output=raw_output,
#                 error_message=str(first_error),
#             )

#             repaired_output = self._run_llm_generate(repair_prompt, json_mode=True)
#             (debug_dir / f"{uiux_version}_uiux_plan_repaired.json.txt").write_text(
#                 repaired_output,
#                 encoding="utf-8",
#             )

#             return parse_uiux_plan(repaired_output)

# def _generate_wireframe_html_with_llm(
#     self,
#     project_name: str,
#     screen,
#     srs: dict,
#     domain_pack: dict,
#     sds: dict,
#     api_contract: dict,
#     db_pack: dict,
#     all_screens: list[dict],
#     user_prompt: str | None,
#     uiux_version: str,
# ) -> str:
#     """
#     Generates one high-fidelity wireframe using Ollama.

#     Attempts:
#     1. Normal high-fidelity prompt
#     2. Repair prompt
#     3. Final strict regeneration prompt

#     No predefined UI template is used.
#     """

#     debug_dir = self.output_dir / "debug" / "uiux"
#     debug_dir.mkdir(parents=True, exist_ok=True)

#     first_error = None
#     second_error = None

#     # ---------------------------------------------------------
#     # Attempt 1: normal high-fidelity generation
#     # ---------------------------------------------------------
#     prompt = build_high_fidelity_wireframe_prompt(
#         project_name=project_name,
#         screen=screen,
#         srs=srs,
#         domain_pack=domain_pack,
#         sds=sds,
#         api_contract=api_contract,
#         db_pack=db_pack,
#         all_screens=all_screens,
#         user_prompt=user_prompt,
#     )

#     raw_output = self._run_llm_generate(prompt)

#     raw_debug_path = debug_dir / f"{uiux_version}_{screen.id}_attempt1_raw.html.txt"
#     raw_debug_path.write_text(raw_output or "", encoding="utf-8")

#     try:
#         return clean_html_output(raw_output)

#     except WireframeParseError as error:
#         first_error = error
#         print(f"[WARN] Attempt 1 failed for {screen.id}: {error}")

#     # ---------------------------------------------------------
#     # Attempt 2: repair previous output
#     # ---------------------------------------------------------
#     repair_prompt = build_wireframe_repair_prompt(
#         screen=screen,
#         invalid_output=raw_output or "",
#         error_message=str(first_error),
#     )

#     repaired_output = self._run_llm_generate(repair_prompt)

#     repaired_debug_path = debug_dir / f"{uiux_version}_{screen.id}_attempt2_repaired.html.txt"
#     repaired_debug_path.write_text(repaired_output or "", encoding="utf-8")

#     try:
#         return clean_html_output(repaired_output)

#     except WireframeParseError as error:
#         second_error = error
#         print(f"[WARN] Attempt 2 failed for {screen.id}: {error}")

#     # ---------------------------------------------------------
#     # Attempt 3: final strict regeneration
#     # ---------------------------------------------------------
#     final_prompt = build_final_html_regeneration_prompt(
#         screen=screen,
#         project_name=project_name,
#         user_prompt=user_prompt,
#     )

#     final_output = self._run_llm_generate(final_prompt)

#     final_debug_path = debug_dir / f"{uiux_version}_{screen.id}_attempt3_final.html.txt"
#     final_debug_path.write_text(final_output or "", encoding="utf-8")

#     try:
#         return clean_html_output(final_output)

#     except WireframeParseError as third_error:
#         raise WireframeParseError(
#             f"Failed to generate usable HTML for {screen.id} - {screen.name} after 3 LLM attempts. "
#             f"Attempt 1 debug: {raw_debug_path}. "
#             f"Attempt 2 debug: {repaired_debug_path}. "
#             f"Attempt 3 debug: {final_debug_path}. "
#             f"Attempt 1 error: {first_error}. "
#             f"Attempt 2 error: {second_error}. "
#             f"Final error: {third_error}"
#         ) from third_error

#     def generate_design_pack(
#         self,
#         run_id: str,
#         srs_version: str = "v1",
#         domain_version: str = "v1",
#         architecture_version: str = "v1",
#         uiux_version: str = "v1",
#         include_admin: bool = True,
#         render_images: bool = True,
#         user_prompt: str | None = None,
#         change_request: str | None = None,
#         status: str = "generated",
#         previous_version: str | None = None,
#     ) -> dict:
#         srs, domain_pack, sds, api_contract, db_pack = self.load_approved_inputs(
#             run_id=run_id,
#             srs_version=srs_version,
#             domain_version=domain_version,
#             architecture_version=architecture_version,
#         )

#         validation = self.validate_inputs(
#             srs=srs,
#             domain_pack=domain_pack,
#             sds=sds,
#             api_contract=api_contract,
#             db_pack=db_pack,
#         )

#         if not validation["valid"]:
#             return validation

#         project_name = srs.get("project_name", "AutoForge E-commerce Platform")
#         combined_prompt = user_prompt or change_request

#         base_dir = self.output_dir / "runs" / run_id / "uiux" / uiux_version
#         flows_dir = base_dir / "flows"
#         wireframes_dir = base_dir / "wireframes"

#         flows_dir.mkdir(parents=True, exist_ok=True)
#         wireframes_dir.mkdir(parents=True, exist_ok=True)

#         screens, user_flows, traceability = self._generate_uiux_plan_with_llm(
#             project_name=project_name,
#             srs=srs,
#             domain_pack=domain_pack,
#             sds=sds,
#             api_contract=api_contract,
#             db_pack=db_pack,
#             uiux_version=uiux_version,
#             user_prompt=combined_prompt,
#         )

#         primary_flow = user_flows[0]
#         mermaid = build_mermaid_from_flow(primary_flow)

#         flow_json_path = flows_dir / f"user_flows_{uiux_version}.json"
#         flow_mmd_path = flows_dir / f"user_flows_{uiux_version}.mmd"

#         flow_json_path.write_text(
#             json.dumps(primary_flow.model_dump(), indent=2),
#             encoding="utf-8",
#         )
#         flow_mmd_path.write_text(mermaid, encoding="utf-8")

#         flow_png_path = None
#         if render_images:
#             flow_png_path = render_mermaid_to_png(flow_mmd_path)

#         wireframe_html_paths = []
#         wireframe_png_paths = []
#         all_screens_data = [screen.model_dump() for screen in screens]

#         for screen in screens:
#             html_path = wireframes_dir / screen.file_name

#             html = self._generate_wireframe_html_with_llm(
#                 project_name=project_name,
#                 screen=screen,
#                 srs=srs,
#                 domain_pack=domain_pack,
#                 sds=sds,
#                 api_contract=api_contract,
#                 db_pack=db_pack,
#                 all_screens=all_screens_data,
#                 user_prompt=combined_prompt,
#                 uiux_version=uiux_version,
#             )

#             html_path.write_text(html, encoding="utf-8")
#             wireframe_html_paths.append(str(html_path))

#             if render_images:
#                 png_path = html_path.with_suffix(".png")
#                 rendered = render_html_to_png(html_path, png_path)
#                 if rendered:
#                     wireframe_png_paths.append(rendered)

#         wireframe_spec = WireframeSpec(
#             version=uiux_version,
#             screens=screens,
#         )

#         wireframes_json_path = wireframes_dir / f"wireframes_{uiux_version}.json"
#         wireframes_json_path.write_text(
#             json.dumps(wireframe_spec.model_dump(), indent=2),
#             encoding="utf-8",
#         )

#         trace_path = base_dir / f"trace_uiux_{uiux_version}.json"
#         trace_path.write_text(
#             json.dumps([link.model_dump() for link in traceability], indent=2),
#             encoding="utf-8",
#         )

#         uiux_pack = UIUXPack(
#             project_name=project_name,
#             version=uiux_version,
#             source_srs_version=srs_version,
#             source_api_version=architecture_version,
#             status=status,
#             screens=screens,
#             user_flows=user_flows,
#             traceability=traceability,
#             flow_mmd_path=str(flow_mmd_path),
#             flow_png_path=flow_png_path,
#             wireframe_html_paths=wireframe_html_paths,
#             wireframe_png_paths=wireframe_png_paths,
#         )

#         pack_json_path = base_dir / f"UIUXPack_{uiux_version}.json"
#         pack_md_path = base_dir / f"UIUXPack_{uiux_version}.md"

#         pack_json_path.write_text(
#             json.dumps(uiux_pack.model_dump(), indent=2),
#             encoding="utf-8",
#         )

#         pack_md_path.write_text(
#             self._render_markdown_summary(
#                 pack=uiux_pack,
#                 domain_version=domain_version,
#                 architecture_version=architecture_version,
#                 user_prompt=combined_prompt,
#                 previous_version=previous_version,
#             ),
#             encoding="utf-8",
#         )

#         revision_note_path = None

#         if previous_version or combined_prompt:
#             revision_note_path = base_dir / f"revision_note_{uiux_version}.txt"
#             revision_note_path.write_text(
#                 f"Previous version: {previous_version or 'N/A'}\n"
#                 f"New version: {uiux_version}\n"
#                 f"User prompt / change request: {combined_prompt or 'N/A'}\n"
#                 f"Generation mode: LLM-only high-fidelity UI/UX generation\n",
#                 encoding="utf-8",
#             )

#         return {
#             "run_id": run_id,
#             "uiux_version": uiux_version,
#             "srs_version": srs_version,
#             "domain_version": domain_version,
#             "architecture_version": architecture_version,
#             "generation_mode": "llm_only_high_fidelity_uiux",
#             "user_prompt": combined_prompt,
#             "uiux_pack_path": str(pack_json_path),
#             "markdown_path": str(pack_md_path),
#             "flow_json_path": str(flow_json_path),
#             "flow_mmd_path": str(flow_mmd_path),
#             "flow_png_path": flow_png_path,
#             "wireframes_json_path": str(wireframes_json_path),
#             "wireframe_html_paths": wireframe_html_paths,
#             "wireframe_png_paths": wireframe_png_paths,
#             "traceability_path": str(trace_path),
#             "revision_note_path": str(revision_note_path) if revision_note_path else None,
#         }

#     def revise_design_pack(
#         self,
#         run_id: str,
#         current_version: str,
#         new_version: str,
#         change_request: str,
#         srs_version: str = "v1",
#         domain_version: str = "v1",
#         architecture_version: str = "v1",
#         include_admin: bool = True,
#         render_images: bool = True,
#     ) -> dict:
#         current_pack_path = (
#             self.output_dir / "runs" / run_id / "uiux" / current_version / f"UIUXPack_{current_version}.json"
#         )

#         if not current_pack_path.exists():
#             raise FileNotFoundError(f"Current UIUXPack not found: {current_pack_path}")

#         return self.generate_design_pack(
#             run_id=run_id,
#             srs_version=srs_version,
#             domain_version=domain_version,
#             architecture_version=architecture_version,
#             uiux_version=new_version,
#             include_admin=include_admin,
#             render_images=render_images,
#             user_prompt=change_request,
#             change_request=change_request,
#             status="revised",
#             previous_version=current_version,
#         )

#     def _render_markdown_summary(
#         self,
#         pack: UIUXPack,
#         domain_version: str,
#         architecture_version: str,
#         user_prompt: str | None = None,
#         previous_version: str | None = None,
#     ) -> str:
#         lines = [
#             f"# UI/UX Design Pack: {pack.project_name}",
#             "",
#             f"**Version:** {pack.version}",
#             f"**Status:** {pack.status}",
#             f"**Source SRS:** {pack.source_srs_version}",
#             f"**Source DomainPack:** {domain_version}",
#             f"**Source Architecture:** {architecture_version}",
#             f"**Generation Mode:** LLM-only high-fidelity UI/UX generation",
#         ]

#         if previous_version:
#             lines.append(f"**Previous Version:** {previous_version}")

#         if user_prompt:
#             lines.extend([
#                 "",
#                 "## User Prompt / Change Request",
#                 user_prompt,
#             ])

#         lines.extend(["", "## Screens"])

#         for screen in pack.screens:
#             lines.append(f"- **{screen.id} — {screen.name}**: {screen.description}")

#         lines.append("")
#         lines.append("## User Flows")

#         for flow in pack.user_flows:
#             lines.append(f"- **{flow.id} — {flow.name}** ({flow.actor})")

#         lines.append("")
#         lines.append("## Traceability")

#         for link in pack.traceability:
#             lines.append(f"- {link.requirement_id} → {link.screen_id} ({link.screen_name})")

#         return "\n".join(lines)

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
    build_uiux_plan_repair_prompt,
    build_high_fidelity_wireframe_prompt,
    build_wireframe_repair_prompt,
    build_final_html_regeneration_prompt,
)
from agents.uiux_agent.parser import (
    parse_uiux_plan,
    clean_html_output,
    UIUXParseError,
    WireframeParseError,
)
from agents.uiux_agent.renderer import render_mermaid_to_png, render_html_to_png


class UIUXAgent:
    """
    LLM-only UI/UX Agent.

    Inputs:
    - Approved SRS
    - Approved DomainPack
    - Approved Architecture output excluding diagrams:
      SDS JSON, OpenAPI YAML, DBPack JSON

    Outputs:
    - LLM-generated screens
    - LLM-generated user flows
    - LLM-generated traceability
    - LLM-generated high-fidelity HTML wireframes
    - PNG screenshots
    """

    def __init__(self, llm_provider=None):
        self.llm_provider = llm_provider
        self.output_dir = Path(os.getenv("OUTPUT_DIR", "outputs"))

    def _run_llm_generate(self, prompt: str, json_mode: bool = False) -> str:
        """
        Supports provider.generate(prompt) and provider.generate(prompt, json_mode=True).
        """

        if not self.llm_provider:
            raise RuntimeError("UI/UX Agent requires an LLM provider.")

        try:
            result = self.llm_provider.generate(prompt, json_mode=json_mode)
        except TypeError:
            result = self.llm_provider.generate(prompt)

        if inspect.isawaitable(result):
            return asyncio.run(result)

        return result

    def _find_file(self, folder: Path, preferred_name: str, fallback_patterns: list[str]) -> Path:
        """
        Finds a required artifact even if the exact file name is slightly different.
        """

        preferred = folder / preferred_name

        if preferred.exists():
            return preferred

        for pattern in fallback_patterns:
            matches = list(folder.glob(pattern))
            if matches:
                return matches[0]

        raise FileNotFoundError(
            f"Could not find {preferred_name} in {folder}. Tried patterns: {fallback_patterns}"
        )

    def load_approved_inputs(
        self,
        run_id: str,
        srs_version: str,
        domain_version: str,
        architecture_version: str,
    ) -> tuple[dict, dict, dict, dict, dict]:
        """
        Loads approved upstream artifacts.
        Architecture diagrams are not loaded.
        """

        run_dir = self.output_dir / "runs" / run_id

        srs_dir = run_dir / "srs" / srs_version
        domain_dir = run_dir / "domain" / domain_version
        architecture_dir = run_dir / "architecture" / architecture_version

        srs_path = self._find_file(
            srs_dir,
            f"SRS_{srs_version}.json",
            ["SRS_*.json", "*.json"],
        )

        domain_path = self._find_file(
            domain_dir,
            f"DomainPack_{domain_version}.json",
            ["DomainPack_*.json", "*.json"],
        )

        sds_path = self._find_file(
            architecture_dir,
            f"SDS_{architecture_version}.json",
            ["SDS_*.json", "*SDS*.json", "*.json"],
        )

        openapi_path = self._find_file(
            architecture_dir,
            f"OpenAPI_{architecture_version}.yaml",
            ["OpenAPI_*.yaml", "*openapi*.yaml", "*.yaml", "*.yml"],
        )

        db_pack_path = self._find_file(
            architecture_dir,
            f"DBPack_{architecture_version}.json",
            ["DBPack_*.json", "*DB*.json", "*db*.json"],
        )

        srs = json.loads(srs_path.read_text(encoding="utf-8"))
        domain_pack = json.loads(domain_path.read_text(encoding="utf-8"))
        sds = json.loads(sds_path.read_text(encoding="utf-8"))
        api_contract = yaml.safe_load(openapi_path.read_text(encoding="utf-8"))
        db_pack = json.loads(db_pack_path.read_text(encoding="utf-8"))

        return srs, domain_pack, sds, api_contract, db_pack

    def validate_inputs(
        self,
        srs: dict,
        domain_pack: dict,
        sds: dict,
        api_contract: dict,
        db_pack: dict,
    ) -> dict:
        questions = []

        if not srs.get("functional_requirements"):
            questions.append("Approved SRS must contain functional_requirements.")

        if not isinstance(api_contract, dict) or not api_contract.get("paths"):
            questions.append("Approved OpenAPI contract must contain paths.")

        if not sds:
            questions.append("Approved SDS is missing or empty.")

        if not domain_pack:
            questions.append("Approved DomainPack is missing or empty.")

        if not db_pack:
            questions.append("Approved DBPack is missing or empty.")

        if not self.llm_provider:
            questions.append("LLM provider is required for UI/UX generation.")

        return {
            "valid": len(questions) == 0,
            "clarification_required": len(questions) > 0,
            "questions": questions,
        }

    def _generate_uiux_plan_with_llm(
        self,
        project_name: str,
        srs: dict,
        domain_pack: dict,
        sds: dict,
        api_contract: dict,
        db_pack: dict,
        uiux_version: str,
        user_prompt: str | None,
    ):
        """
        Generates UI screens, user flows, and traceability using the LLM.
        """

        prompt = build_uiux_plan_prompt(
            project_name=project_name,
            srs=srs,
            domain_pack=domain_pack,
            sds=sds,
            api_contract=api_contract,
            db_pack=db_pack,
            uiux_version=uiux_version,
            user_prompt=user_prompt,
        )

        debug_dir = self.output_dir / "debug" / "uiux"
        debug_dir.mkdir(parents=True, exist_ok=True)

        raw_output = self._run_llm_generate(prompt, json_mode=True)

        (debug_dir / f"{uiux_version}_uiux_plan_raw.json.txt").write_text(
            raw_output or "",
            encoding="utf-8",
        )

        try:
            return parse_uiux_plan(raw_output)

        except UIUXParseError as first_error:
            repair_prompt = build_uiux_plan_repair_prompt(
                invalid_output=raw_output or "",
                error_message=str(first_error),
            )

            repaired_output = self._run_llm_generate(repair_prompt, json_mode=True)

            (debug_dir / f"{uiux_version}_uiux_plan_repaired.json.txt").write_text(
                repaired_output or "",
                encoding="utf-8",
            )

            return parse_uiux_plan(repaired_output)

    def _generate_wireframe_html_with_llm(
        self,
        project_name: str,
        screen,
        srs: dict,
        domain_pack: dict,
        sds: dict,
        api_contract: dict,
        db_pack: dict,
        all_screens: list[dict],
        user_prompt: str | None,
        uiux_version: str,
    ) -> str:
        """
        Generates one high-fidelity wireframe using Ollama.

        Attempts:
        1. Normal high-fidelity prompt
        2. Repair prompt
        3. Final strict regeneration prompt

        No predefined UI template is used.
        """

        debug_dir = self.output_dir / "debug" / "uiux"
        debug_dir.mkdir(parents=True, exist_ok=True)

        first_error = None
        second_error = None

        # Attempt 1
        prompt = build_high_fidelity_wireframe_prompt(
            project_name=project_name,
            screen=screen,
            srs=srs,
            domain_pack=domain_pack,
            sds=sds,
            api_contract=api_contract,
            db_pack=db_pack,
            all_screens=all_screens,
            user_prompt=user_prompt,
        )

        raw_output = self._run_llm_generate(prompt)

        raw_debug_path = debug_dir / f"{uiux_version}_{screen.id}_attempt1_raw.html.txt"
        raw_debug_path.write_text(raw_output or "", encoding="utf-8")

        try:
            return clean_html_output(raw_output)

        except WireframeParseError as error:
            first_error = error
            print(f"[WARN] Attempt 1 failed for {screen.id}: {error}")

        # Attempt 2
        repair_prompt = build_wireframe_repair_prompt(
            screen=screen,
            invalid_output=raw_output or "",
            error_message=str(first_error),
        )

        repaired_output = self._run_llm_generate(repair_prompt)

        repaired_debug_path = debug_dir / f"{uiux_version}_{screen.id}_attempt2_repaired.html.txt"
        repaired_debug_path.write_text(repaired_output or "", encoding="utf-8")

        try:
            return clean_html_output(repaired_output)

        except WireframeParseError as error:
            second_error = error
            print(f"[WARN] Attempt 2 failed for {screen.id}: {error}")

        # Attempt 3
        final_prompt = build_final_html_regeneration_prompt(
            screen=screen,
            project_name=project_name,
            user_prompt=user_prompt,
        )

        final_output = self._run_llm_generate(final_prompt)

        final_debug_path = debug_dir / f"{uiux_version}_{screen.id}_attempt3_final.html.txt"
        final_debug_path.write_text(final_output or "", encoding="utf-8")

        try:
            return clean_html_output(final_output)

        except WireframeParseError as third_error:
            raise WireframeParseError(
                f"Failed to generate usable HTML for {screen.id} - {screen.name} after 3 LLM attempts. "
                f"Attempt 1 debug: {raw_debug_path}. "
                f"Attempt 2 debug: {repaired_debug_path}. "
                f"Attempt 3 debug: {final_debug_path}. "
                f"Attempt 1 error: {first_error}. "
                f"Attempt 2 error: {second_error}. "
                f"Final error: {third_error}"
            ) from third_error

    def generate_design_pack(
        self,
        run_id: str,
        srs_version: str = "v1",
        domain_version: str = "v1",
        architecture_version: str = "v1",
        uiux_version: str = "v1",
        include_admin: bool = True,
        render_images: bool = True,
        user_prompt: str | None = None,
        change_request: str | None = None,
        status: str = "generated",
        previous_version: str | None = None,
    ) -> dict:
        """
        Generates the full UI/UX design pack.
        """

        srs, domain_pack, sds, api_contract, db_pack = self.load_approved_inputs(
            run_id=run_id,
            srs_version=srs_version,
            domain_version=domain_version,
            architecture_version=architecture_version,
        )

        validation = self.validate_inputs(
            srs=srs,
            domain_pack=domain_pack,
            sds=sds,
            api_contract=api_contract,
            db_pack=db_pack,
        )

        if not validation["valid"]:
            return validation

        project_name = srs.get("project_name", "AutoForge E-commerce Platform")
        combined_prompt = user_prompt or change_request

        base_dir = self.output_dir / "runs" / run_id / "uiux" / uiux_version
        flows_dir = base_dir / "flows"
        wireframes_dir = base_dir / "wireframes"

        flows_dir.mkdir(parents=True, exist_ok=True)
        wireframes_dir.mkdir(parents=True, exist_ok=True)

        screens, user_flows, traceability = self._generate_uiux_plan_with_llm(
            project_name=project_name,
            srs=srs,
            domain_pack=domain_pack,
            sds=sds,
            api_contract=api_contract,
            db_pack=db_pack,
            uiux_version=uiux_version,
            user_prompt=combined_prompt,
        )

        if len(screens) < 1:
            raise ValueError("LLM generated zero UI screens.")

        primary_flow = user_flows[0]
        mermaid = build_mermaid_from_flow(primary_flow)

        flow_json_path = flows_dir / f"user_flows_{uiux_version}.json"
        flow_mmd_path = flows_dir / f"user_flows_{uiux_version}.mmd"

        flow_json_path.write_text(
            json.dumps(primary_flow.model_dump(), indent=2),
            encoding="utf-8",
        )

        flow_mmd_path.write_text(
            mermaid,
            encoding="utf-8",
        )

        flow_png_path = None

        if render_images:
            flow_png_path = render_mermaid_to_png(flow_mmd_path)

        wireframe_html_paths = []
        wireframe_png_paths = []

        all_screens_data = [screen.model_dump() for screen in screens]

        for screen in screens:
            html_path = wireframes_dir / screen.file_name

            html = self._generate_wireframe_html_with_llm(
                project_name=project_name,
                screen=screen,
                srs=srs,
                domain_pack=domain_pack,
                sds=sds,
                api_contract=api_contract,
                db_pack=db_pack,
                all_screens=all_screens_data,
                user_prompt=combined_prompt,
                uiux_version=uiux_version,
            )

            html_path.write_text(html, encoding="utf-8")
            wireframe_html_paths.append(str(html_path))

            if render_images:
                png_path = html_path.with_suffix(".png")
                rendered = render_html_to_png(html_path, png_path)

                if rendered:
                    wireframe_png_paths.append(rendered)

        wireframe_spec = WireframeSpec(
            version=uiux_version,
            screens=screens,
        )

        wireframes_json_path = wireframes_dir / f"wireframes_{uiux_version}.json"

        wireframes_json_path.write_text(
            json.dumps(wireframe_spec.model_dump(), indent=2),
            encoding="utf-8",
        )

        trace_path = base_dir / f"trace_uiux_{uiux_version}.json"

        trace_path.write_text(
            json.dumps([link.model_dump() for link in traceability], indent=2),
            encoding="utf-8",
        )

        uiux_pack = UIUXPack(
            project_name=project_name,
            version=uiux_version,
            source_srs_version=srs_version,
            source_api_version=architecture_version,
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
                domain_version=domain_version,
                architecture_version=architecture_version,
                user_prompt=combined_prompt,
                previous_version=previous_version,
            ),
            encoding="utf-8",
        )

        revision_note_path = None

        if previous_version or combined_prompt:
            revision_note_path = base_dir / f"revision_note_{uiux_version}.txt"
            revision_note_path.write_text(
                f"Previous version: {previous_version or 'N/A'}\n"
                f"New version: {uiux_version}\n"
                f"User prompt / change request: {combined_prompt or 'N/A'}\n"
                f"Generation mode: LLM-only high-fidelity UI/UX generation\n",
                encoding="utf-8",
            )

        return {
            "run_id": run_id,
            "uiux_version": uiux_version,
            "srs_version": srs_version,
            "domain_version": domain_version,
            "architecture_version": architecture_version,
            "generation_mode": "llm_only_high_fidelity_uiux",
            "user_prompt": combined_prompt,
            "uiux_pack_path": str(pack_json_path),
            "markdown_path": str(pack_md_path),
            "flow_json_path": str(flow_json_path),
            "flow_mmd_path": str(flow_mmd_path),
            "flow_png_path": flow_png_path,
            "wireframes_json_path": str(wireframes_json_path),
            "wireframe_html_paths": wireframe_html_paths,
            "wireframe_png_paths": wireframe_png_paths,
            "traceability_path": str(trace_path),
            "revision_note_path": str(revision_note_path) if revision_note_path else None,
        }

    def revise_design_pack(
        self,
        run_id: str,
        current_version: str,
        new_version: str,
        change_request: str,
        srs_version: str = "v1",
        domain_version: str = "v1",
        architecture_version: str = "v1",
        include_admin: bool = True,
        render_images: bool = True,
    ) -> dict:
        """
        Revises the UI/UX design pack and saves it as a new version.
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
            domain_version=domain_version,
            architecture_version=architecture_version,
            uiux_version=new_version,
            include_admin=include_admin,
            render_images=render_images,
            user_prompt=change_request,
            change_request=change_request,
            status="revised",
            previous_version=current_version,
        )

    def _render_markdown_summary(
        self,
        pack: UIUXPack,
        domain_version: str,
        architecture_version: str,
        user_prompt: str | None = None,
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
            f"**Source SRS:** {pack.source_srs_version}",
            f"**Source DomainPack:** {domain_version}",
            f"**Source Architecture:** {architecture_version}",
            f"**Generation Mode:** LLM-only high-fidelity UI/UX generation",
        ]

        if previous_version:
            lines.append(f"**Previous Version:** {previous_version}")

        if user_prompt:
            lines.extend(
                [
                    "",
                    "## User Prompt / Change Request",
                    user_prompt,
                ]
            )

        lines.extend(["", "## Screens"])

        for screen in pack.screens:
            lines.append(f"- **{screen.id} — {screen.name}**: {screen.description}")

        lines.append("")
        lines.append("## User Flows")

        for flow in pack.user_flows:
            lines.append(f"- **{flow.id} — {flow.name}** ({flow.actor})")

        lines.append("")
        lines.append("## Traceability")

        for link in pack.traceability:
            lines.append(
                f"- {link.requirement_id} → {link.screen_id} ({link.screen_name})"
            )

        return "\n".join(lines)