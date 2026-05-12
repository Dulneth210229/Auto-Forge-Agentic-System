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
    Split-workflow UI/UX Agent for AutoForge.

    Main goal:
    - Avoid one very long /uiux/designpack/generate request.
    - Generate UI/UX in controllable stages.
    - Still generate PNG wireframes.
    - Save progress screen by screen.
    - Skip already-generated screens when rerunning.
    - Support orchestrator usage through run_id + uiux_version.

    Split workflow:
    1. generate_plan()
       - Generates screens, user flows, traceability.
       - Saves uiux_plan_vX.json, user flow JSON/MMD/PNG, traceability JSON.

    2. generate_all_wireframes()
       - Reads saved plan.
       - Generates all wireframes screen by screen.
       - Saves HTML and PNG immediately per screen.
       - Can skip already-generated screens.

    3. finalize_design_pack()
       - Does not call Ollama.
       - Packages already-created artifacts into UIUXPack JSON/Markdown.

    4. revise_design_pack()
       - Creates a new UI/UX version using a user change request.
    """

    def __init__(self, llm_provider=None):
        self.llm_provider = llm_provider
        self.output_dir = Path(os.getenv("OUTPUT_DIR", "outputs"))

    # ------------------------------------------------------------------
    # Common helpers
    # ------------------------------------------------------------------

    def _run_llm_generate(self, prompt: str, json_mode: bool = False) -> str:
        """
        Calls the configured LLM provider.

        Supports:
        - provider.generate(prompt)
        - provider.generate(prompt, json_mode=True)
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

    def _find_file(
        self,
        folder: Path,
        preferred_name: str,
        fallback_patterns: list[str],
    ) -> Path:
        """
        Finds a required artifact even if the exact filename is slightly different.
        """

        preferred = folder / preferred_name

        if preferred.exists():
            return preferred

        for pattern in fallback_patterns:
            matches = list(folder.glob(pattern))
            if matches:
                return matches[0]

        raise FileNotFoundError(
            f"Could not find {preferred_name} in {folder}. "
            f"Tried patterns: {fallback_patterns}"
        )

    def _uiux_base_dir(self, run_id: str, uiux_version: str) -> Path:
        return self.output_dir / "runs" / run_id / "uiux" / uiux_version

    def _flows_dir(self, run_id: str, uiux_version: str) -> Path:
        return self._uiux_base_dir(run_id, uiux_version) / "flows"

    def _wireframes_dir(self, run_id: str, uiux_version: str) -> Path:
        return self._uiux_base_dir(run_id, uiux_version) / "wireframes"

    def _plan_path(self, run_id: str, uiux_version: str) -> Path:
        return self._uiux_base_dir(run_id, uiux_version) / f"uiux_plan_{uiux_version}.json"

    def _trace_path(self, run_id: str, uiux_version: str) -> Path:
        return self._uiux_base_dir(run_id, uiux_version) / f"trace_uiux_{uiux_version}.json"

    def _debug_dir(self) -> Path:
        path = self.output_dir / "debug" / "uiux"
        path.mkdir(parents=True, exist_ok=True)
        return path

    # ------------------------------------------------------------------
    # Input loading and validation
    # ------------------------------------------------------------------

    def load_approved_inputs(
        self,
        run_id: str,
        srs_version: str,
        domain_version: str,
        architecture_version: str,
    ) -> tuple[dict, dict, dict, dict, dict]:
        """
        Loads approved upstream artifacts.

        Required files:
        outputs/runs/<RUN_ID>/srs/<SRS_VERSION>/SRS_<SRS_VERSION>.json
        outputs/runs/<RUN_ID>/domain/<DOMAIN_VERSION>/DomainPack_<DOMAIN_VERSION>.json
        outputs/runs/<RUN_ID>/architecture/<ARCH_VERSION>/SDS_<ARCH_VERSION>.json
        outputs/runs/<RUN_ID>/architecture/<ARCH_VERSION>/OpenAPI_<ARCH_VERSION>.yaml
        outputs/runs/<RUN_ID>/architecture/<ARCH_VERSION>/DBPack_<ARCH_VERSION>.json

        Architecture diagrams are intentionally not loaded.
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
        """
        Validates all required approved artifacts for UI/UX generation.
        """

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

    def validate_approved_inputs(
        self,
        run_id: str,
        srs_version: str = "v1",
        domain_version: str = "v1",
        architecture_version: str = "v1",
    ) -> dict:
        """
        Loads and validates approved inputs.
        Useful for /uiux/srs/validate endpoint.
        """

        srs, domain_pack, sds, api_contract, db_pack = self.load_approved_inputs(
            run_id=run_id,
            srs_version=srs_version,
            domain_version=domain_version,
            architecture_version=architecture_version,
        )

        return self.validate_inputs(
            srs=srs,
            domain_pack=domain_pack,
            sds=sds,
            api_contract=api_contract,
            db_pack=db_pack,
        )

    # ------------------------------------------------------------------
    # Step 1: Plan generation
    # ------------------------------------------------------------------

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
        Generates screens, user flows, and traceability using Ollama.

        The first attempt uses JSON mode.
        If the output is invalid, a repair prompt is used.
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

        debug_dir = self._debug_dir()

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

    def generate_plan(
        self,
        run_id: str,
        srs_version: str = "v1",
        domain_version: str = "v1",
        architecture_version: str = "v1",
        uiux_version: str = "v1",
        include_admin: bool = True,
        render_images: bool = True,
        user_prompt: str | None = None,
        status: str = "plan_generated",
        previous_version: str | None = None,
    ) -> dict:
        """
        Step 1:
        Generates UI/UX plan only.

        Saves:
        - uiux_plan_vX.json
        - user_flows_vX.json
        - user_flows_vX.mmd
        - user_flows_vX.png if render_images=True
        - trace_uiux_vX.json
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

        base_dir = self._uiux_base_dir(run_id, uiux_version)
        flows_dir = self._flows_dir(run_id, uiux_version)

        base_dir.mkdir(parents=True, exist_ok=True)
        flows_dir.mkdir(parents=True, exist_ok=True)

        screens, user_flows, traceability = self._generate_uiux_plan_with_llm(
            project_name=project_name,
            srs=srs,
            domain_pack=domain_pack,
            sds=sds,
            api_contract=api_contract,
            db_pack=db_pack,
            uiux_version=uiux_version,
            user_prompt=user_prompt,
        )

        if len(screens) < 1:
            raise ValueError("LLM generated zero UI screens.")

        primary_flow = user_flows[0]
        mermaid = build_mermaid_from_flow(primary_flow)

        plan_data = {
            "project_name": project_name,
            "version": uiux_version,
            "status": status,
            "source_srs_version": srs_version,
            "source_domain_version": domain_version,
            "source_architecture_version": architecture_version,
            "previous_version": previous_version,
            "user_prompt": user_prompt,
            "screens": [screen.model_dump() for screen in screens],
            "user_flows": [flow.model_dump() for flow in user_flows],
            "traceability": [link.model_dump() for link in traceability],
        }

        plan_path = self._plan_path(run_id, uiux_version)
        flow_json_path = flows_dir / f"user_flows_{uiux_version}.json"
        flow_mmd_path = flows_dir / f"user_flows_{uiux_version}.mmd"
        trace_path = self._trace_path(run_id, uiux_version)

        plan_path.write_text(
            json.dumps(plan_data, indent=2),
            encoding="utf-8",
        )

        flow_json_path.write_text(
            json.dumps(primary_flow.model_dump(), indent=2),
            encoding="utf-8",
        )

        flow_mmd_path.write_text(
            mermaid,
            encoding="utf-8",
        )

        trace_path.write_text(
            json.dumps([link.model_dump() for link in traceability], indent=2),
            encoding="utf-8",
        )

        flow_png_path = None
        if render_images:
            flow_png_path = render_mermaid_to_png(flow_mmd_path)

        return {
            "status": "success",
            "stage": "uiux_plan",
            "run_id": run_id,
            "uiux_version": uiux_version,
            "screen_count": len(screens),
            "flow_count": len(user_flows),
            "traceability_count": len(traceability),
            "plan_path": str(plan_path),
            "flow_json_path": str(flow_json_path),
            "flow_mmd_path": str(flow_mmd_path),
            "flow_png_path": flow_png_path,
            "traceability_path": str(trace_path),
            "next_step": "Call POST /uiux/wireframes/generate-all or use /orchestrator/uiux/run",
        }

    # ------------------------------------------------------------------
    # Step 2: Wireframe generation
    # ------------------------------------------------------------------

    def _load_plan(self, run_id: str, uiux_version: str) -> dict:
        """
        Loads saved UI/UX plan.
        """

        plan_path = self._plan_path(run_id, uiux_version)

        if not plan_path.exists():
            raise FileNotFoundError(
                f"UI/UX plan not found: {plan_path}. "
                "Run POST /uiux/plan/generate first."
            )

        return json.loads(plan_path.read_text(encoding="utf-8"))

    def _wireframe_artifacts_exist(
        self,
        wireframes_dir: Path,
        screen,
        render_images: bool,
    ) -> bool:
        """
        Checks whether a screen wireframe is already generated.

        This allows generation to resume without redoing completed screens.
        """

        html_path = wireframes_dir / screen.file_name
        png_path = html_path.with_suffix(".png")

        if render_images:
            return html_path.exists() and png_path.exists()

        return html_path.exists()

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

        debug_dir = self._debug_dir()

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

    def generate_all_wireframes(
        self,
        run_id: str,
        srs_version: str = "v1",
        domain_version: str = "v1",
        architecture_version: str = "v1",
        uiux_version: str = "v1",
        render_images: bool = True,
        user_prompt: str | None = None,
        fail_fast: bool = False,
        skip_existing: bool = True,
        max_screens: int | None = None,
    ) -> dict:
        """
        Step 2:
        Generates all wireframes from the saved UI/UX plan.

        Optimizations:
        - Reads saved plan from /uiux/plan/generate.
        - Generates screen by screen.
        - Saves HTML immediately.
        - Saves PNG immediately.
        - Can skip already-generated screens.
        - Can limit max_screens during testing.
        - Can continue on failures when fail_fast=False.
        """

        plan = self._load_plan(run_id, uiux_version)

        srs, domain_pack, sds, api_contract, db_pack = self.load_approved_inputs(
            run_id=run_id,
            srs_version=srs_version,
            domain_version=domain_version,
            architecture_version=architecture_version,
        )

        from agents.uiux_agent.schemas import UIScreen

        screens = [
            UIScreen.model_validate(screen_data)
            for screen_data in plan.get("screens", [])
        ]

        if not screens:
            raise ValueError(
                f"No screens found in UI/UX plan for {run_id}/{uiux_version}."
            )

        if max_screens:
            screens = screens[:max_screens]

        project_name = plan.get("project_name") or srs.get(
            "project_name",
            "AutoForge E-commerce Platform",
        )

        combined_prompt = user_prompt or plan.get("user_prompt")

        wireframes_dir = self._wireframes_dir(run_id, uiux_version)
        wireframes_dir.mkdir(parents=True, exist_ok=True)

        generated = []
        skipped = []
        failed = []
        wireframe_html_paths = []
        wireframe_png_paths = []

        all_screens_data = [screen.model_dump() for screen in screens]

        for index, screen in enumerate(screens, start=1):
            html_path = wireframes_dir / screen.file_name
            png_path = html_path.with_suffix(".png")

            try:
                if skip_existing and self._wireframe_artifacts_exist(
                    wireframes_dir=wireframes_dir,
                    screen=screen,
                    render_images=render_images,
                ):
                    skipped.append(
                        {
                            "screen_id": screen.id,
                            "screen_name": screen.name,
                            "html_path": str(html_path),
                            "png_path": str(png_path) if png_path.exists() else None,
                            "reason": "Already generated. Skipped to save time.",
                        }
                    )

                    wireframe_html_paths.append(str(html_path))

                    if png_path.exists():
                        wireframe_png_paths.append(str(png_path))

                    continue

                print(
                    f"[UIUX] Generating wireframe {index}/{len(screens)}: "
                    f"{screen.id} - {screen.name}"
                )

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

                rendered_png_path = None

                if render_images:
                    rendered = render_html_to_png(html_path, png_path)

                    if rendered:
                        rendered_png_path = rendered
                        wireframe_png_paths.append(rendered)

                generated.append(
                    {
                        "screen_id": screen.id,
                        "screen_name": screen.name,
                        "html_path": str(html_path),
                        "png_path": rendered_png_path,
                    }
                )

            except Exception as error:
                failed_item = {
                    "screen_id": screen.id,
                    "screen_name": screen.name,
                    "error": f"{type(error).__name__}: {str(error)}",
                }

                failed.append(failed_item)

                print(
                    f"[UIUX][WARN] Failed wireframe for {screen.id} - {screen.name}: "
                    f"{failed_item['error']}"
                )

                if fail_fast:
                    raise

        wireframe_spec = WireframeSpec(
            version=uiux_version,
            screens=screens,
        )

        wireframes_json_path = wireframes_dir / f"wireframes_{uiux_version}.json"
        wireframes_json_path.write_text(
            json.dumps(wireframe_spec.model_dump(), indent=2),
            encoding="utf-8",
        )

        status = "success" if not failed else "partial_success"

        return {
            "status": status,
            "stage": "wireframes",
            "run_id": run_id,
            "uiux_version": uiux_version,
            "total_screens": len(screens),
            "generated_count": len(generated),
            "skipped_count": len(skipped),
            "failed_count": len(failed),
            "generated": generated,
            "skipped": skipped,
            "failed": failed,
            "wireframes_json_path": str(wireframes_json_path),
            "wireframe_html_paths": wireframe_html_paths,
            "wireframe_png_paths": wireframe_png_paths,
            "next_step": "Call POST /uiux/designpack/finalize",
        }

    # ------------------------------------------------------------------
    # Step 3: Finalize design pack
    # ------------------------------------------------------------------

    def finalize_design_pack(
        self,
        run_id: str,
        srs_version: str = "v1",
        domain_version: str = "v1",
        architecture_version: str = "v1",
        uiux_version: str = "v1",
        status: str = "finalized",
        previous_version: str | None = None,
    ) -> dict:
        """
        Step 3:
        Finalizes UIUXPack from already-generated artifacts.

        This method does not call Ollama.
        """

        plan = self._load_plan(run_id, uiux_version)

        base_dir = self._uiux_base_dir(run_id, uiux_version)
        flows_dir = self._flows_dir(run_id, uiux_version)
        wireframes_dir = self._wireframes_dir(run_id, uiux_version)

        flow_json_path = flows_dir / f"user_flows_{uiux_version}.json"
        flow_mmd_path = flows_dir / f"user_flows_{uiux_version}.mmd"
        flow_png_path = flows_dir / f"user_flows_{uiux_version}.png"
        trace_path = self._trace_path(run_id, uiux_version)
        wireframes_json_path = wireframes_dir / f"wireframes_{uiux_version}.json"

        if not flow_json_path.exists():
            raise FileNotFoundError(f"Flow JSON not found: {flow_json_path}")

        if not trace_path.exists():
            raise FileNotFoundError(f"Traceability JSON not found: {trace_path}")

        if not wireframes_json_path.exists():
            raise FileNotFoundError(
                f"Wireframes JSON not found: {wireframes_json_path}. "
                "Run POST /uiux/wireframes/generate-all first."
            )

        from agents.uiux_agent.schemas import UIScreen, UserFlow, UITraceLink

        screens = [
            UIScreen.model_validate(screen_data)
            for screen_data in plan.get("screens", [])
        ]

        user_flows = [
            UserFlow.model_validate(flow_data)
            for flow_data in plan.get("user_flows", [])
        ]

        traceability = [
            UITraceLink.model_validate(link_data)
            for link_data in plan.get("traceability", [])
        ]

        html_paths = sorted([str(path) for path in wireframes_dir.glob("*.html")])
        png_paths = sorted([str(path) for path in wireframes_dir.glob("*.png")])

        uiux_pack = UIUXPack(
            project_name=plan.get("project_name", "AutoForge E-commerce Platform"),
            version=uiux_version,
            source_srs_version=srs_version,
            source_api_version=architecture_version,
            status=status,
            screens=screens,
            user_flows=user_flows,
            traceability=traceability,
            flow_mmd_path=str(flow_mmd_path),
            flow_png_path=str(flow_png_path) if flow_png_path.exists() else None,
            wireframe_html_paths=html_paths,
            wireframe_png_paths=png_paths,
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
                user_prompt=plan.get("user_prompt"),
                previous_version=previous_version or plan.get("previous_version"),
            ),
            encoding="utf-8",
        )

        return {
            "status": "success",
            "stage": "finalize",
            "run_id": run_id,
            "uiux_version": uiux_version,
            "uiux_pack_path": str(pack_json_path),
            "markdown_path": str(pack_md_path),
            "flow_mmd_path": str(flow_mmd_path),
            "flow_png_path": str(flow_png_path) if flow_png_path.exists() else None,
            "wireframe_html_count": len(html_paths),
            "wireframe_png_count": len(png_paths),
            "wireframe_html_paths": html_paths,
            "wireframe_png_paths": png_paths,
        }

    # ------------------------------------------------------------------
    # Revision workflow
    # ------------------------------------------------------------------

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
        fail_fast: bool = False,
        skip_existing: bool = True,
        max_screens: int | None = None,
    ) -> dict:
        """
        Revises UI/UX by generating a new version.

        Internal workflow:
        1. Generate revised plan
        2. Generate all revised wireframes
        3. Finalize revised UIUXPack
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

        plan_result = self.generate_plan(
            run_id=run_id,
            srs_version=srs_version,
            domain_version=domain_version,
            architecture_version=architecture_version,
            uiux_version=new_version,
            include_admin=include_admin,
            render_images=render_images,
            user_prompt=change_request,
            status="revised_plan_generated",
            previous_version=current_version,
        )

        wireframe_result = self.generate_all_wireframes(
            run_id=run_id,
            srs_version=srs_version,
            domain_version=domain_version,
            architecture_version=architecture_version,
            uiux_version=new_version,
            render_images=render_images,
            user_prompt=change_request,
            fail_fast=fail_fast,
            skip_existing=skip_existing,
            max_screens=max_screens,
        )

        finalize_result = self.finalize_design_pack(
            run_id=run_id,
            srs_version=srs_version,
            domain_version=domain_version,
            architecture_version=architecture_version,
            uiux_version=new_version,
            status="revised",
            previous_version=current_version,
        )

        return {
            "status": "success" if wireframe_result["failed_count"] == 0 else "partial_success",
            "stage": "revision",
            "run_id": run_id,
            "current_version": current_version,
            "new_version": new_version,
            "change_request": change_request,
            "plan_result": plan_result,
            "wireframe_result": wireframe_result,
            "finalize_result": finalize_result,
        }

    # ------------------------------------------------------------------
    # Backward-compatible wrapper
    # ------------------------------------------------------------------

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
        Backward-compatible wrapper.

        This still runs the full workflow in one request.
        For stable testing, use the split endpoints or orchestrator.
        """

        combined_prompt = user_prompt or change_request

        plan_result = self.generate_plan(
            run_id=run_id,
            srs_version=srs_version,
            domain_version=domain_version,
            architecture_version=architecture_version,
            uiux_version=uiux_version,
            include_admin=include_admin,
            render_images=render_images,
            user_prompt=combined_prompt,
            status="plan_generated",
            previous_version=previous_version,
        )

        wireframe_result = self.generate_all_wireframes(
            run_id=run_id,
            srs_version=srs_version,
            domain_version=domain_version,
            architecture_version=architecture_version,
            uiux_version=uiux_version,
            render_images=render_images,
            user_prompt=combined_prompt,
            fail_fast=False,
            skip_existing=True,
        )

        finalize_result = self.finalize_design_pack(
            run_id=run_id,
            srs_version=srs_version,
            domain_version=domain_version,
            architecture_version=architecture_version,
            uiux_version=uiux_version,
            status=status,
            previous_version=previous_version,
        )

        return {
            "status": "success" if wireframe_result["failed_count"] == 0 else "partial_success",
            "stage": "designpack_generate_wrapper",
            "run_id": run_id,
            "uiux_version": uiux_version,
            "message": "This endpoint runs the full workflow. For stability, use /orchestrator/uiux/run.",
            "plan_result": plan_result,
            "wireframe_result": wireframe_result,
            "finalize_result": finalize_result,
        }

    # ------------------------------------------------------------------
    # Markdown rendering
    # ------------------------------------------------------------------

    def _render_markdown_summary(
        self,
        pack: UIUXPack,
        domain_version: str,
        architecture_version: str,
        user_prompt: str | None = None,
        previous_version: str | None = None,
    ) -> str:
        """
        Human-readable UIUXPack summary.
        """

        lines = [
            f"# UI/UX Design Pack: {pack.project_name}",
            "",
            f"**Version:** {pack.version}",
            f"**Status:** {pack.status}",
            f"**Source SRS:** {pack.source_srs_version}",
            f"**Source DomainPack:** {domain_version}",
            f"**Source Architecture:** {architecture_version}",
            f"**Generation Mode:** Split LLM-only high-fidelity UI/UX generation",
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

        lines.append("")
        lines.append("## Generated Artifacts")
        lines.append(f"- Flow Mermaid: `{pack.flow_mmd_path}`")

        if pack.flow_png_path:
            lines.append(f"- Flow PNG: `{pack.flow_png_path}`")

        lines.append(f"- Wireframe HTML files: {len(pack.wireframe_html_paths)}")
        lines.append(f"- Wireframe PNG files: {len(pack.wireframe_png_paths)}")

        return "\n".join(lines)