import json
import re
from pathlib import Path

from .schemas import (
    GeneratedFile,
    ResponsibilitySummary,
    TraceabilityLink,
    InputArtifactSummary,
    CodeManifest,
)
from .patch_policy import is_safe_generated_path
from .prompt import (
    build_backend_prompt,
    build_frontend_prompt,
    build_devops_prompt,
)
from .parser import parse_file_plan, CodeFileParseError


class CoderAgent:
    def __init__(self, output_dir: str = "outputs", llm_provider=None):
        self.output_dir = Path(output_dir)
        self.llm_provider = llm_provider

    # ---------------------------------------------------------
    # Generic file loading helpers
    # ---------------------------------------------------------

    def _load_json_file(self, path: Path, artifact_name: str) -> dict:
        """
        Load a JSON artifact from disk.
        """

        if not path.exists():
            raise FileNotFoundError(f"{artifact_name} not found: {path}")

        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)

    def _load_text_file(self, path: Path, artifact_name: str) -> str:
        """
        Load a text artifact from disk, such as OpenAPI YAML.
        """

        if not path.exists():
            raise FileNotFoundError(f"{artifact_name} not found: {path}")

        with open(path, "r", encoding="utf-8") as f:
            return f.read()

    def _first_existing_path(self, paths: list[Path], artifact_name: str) -> Path:
        """
        Returns the first existing path from possible versioned/non-versioned paths.
        """

        for path in paths:
            if path.exists():
                return path

        checked_paths = "\n".join(str(path) for path in paths)
        raise FileNotFoundError(
            f"{artifact_name} not found. Checked paths:\n{checked_paths}"
        )

    # ---------------------------------------------------------
    # Artifact loading from outputs/
    # ---------------------------------------------------------

    def _load_srs(self, run_id: str, srs_version: str) -> tuple[dict, Path]:
        possible_paths = [
            self.output_dir / "runs" / run_id / "srs" / srs_version / f"SRS_{srs_version}.json",
            self.output_dir / "runs" / run_id / "srs" / srs_version / "SRS.json",
        ]

        path = self._first_existing_path(possible_paths, "SRS")
        return self._load_json_file(path, "SRS"), path

    def _load_domain_pack(self, run_id: str, domain_version: str) -> tuple[dict, Path]:
        possible_paths = [
            self.output_dir / "runs" / run_id / "domain" / domain_version / f"DomainPack_{domain_version}.json",
            self.output_dir / "runs" / run_id / "domain" / domain_version / "DomainPack.json",
        ]

        path = self._first_existing_path(possible_paths, "DomainPack")
        return self._load_json_file(path, "DomainPack"), path

    def _load_sds(self, run_id: str, architecture_version: str) -> tuple[dict, Path]:
        possible_paths = [
            self.output_dir / "runs" / run_id / "architecture" / architecture_version / f"SDS_{architecture_version}.json",
            self.output_dir / "runs" / run_id / "architecture" / architecture_version / "SDS.json",
        ]

        path = self._first_existing_path(possible_paths, "SDS")
        return self._load_json_file(path, "SDS"), path

    def _load_openapi(self, run_id: str, architecture_version: str) -> tuple[str, Path]:
        possible_paths = [
            self.output_dir / "runs" / run_id / "architecture" / architecture_version / f"OpenAPI_{architecture_version}.yaml",
            self.output_dir / "runs" / run_id / "architecture" / architecture_version / f"OpenAPI_{architecture_version}.yml",
            self.output_dir / "runs" / run_id / "architecture" / architecture_version / f"OpenAPI_{architecture_version}.json",
            self.output_dir / "runs" / run_id / "architecture" / architecture_version / "OpenAPI.yaml",
            self.output_dir / "runs" / run_id / "architecture" / architecture_version / "OpenAPI.yml",
            self.output_dir / "runs" / run_id / "architecture" / architecture_version / "OpenAPI.json",
            self.output_dir / "runs" / run_id / "architecture" / architecture_version / "openapi.yaml",
            self.output_dir / "runs" / run_id / "architecture" / architecture_version / "openapi.yml",
            self.output_dir / "runs" / run_id / "architecture" / architecture_version / "openapi.json",
        ]

        path = self._first_existing_path(possible_paths, "API Contract / OpenAPI")
        return self._load_text_file(path, "API Contract / OpenAPI"), path

    def _load_db_pack(self, run_id: str, architecture_version: str) -> tuple[dict, Path]:
        possible_paths = [
            self.output_dir / "runs" / run_id / "architecture" / architecture_version / f"DBPack_{architecture_version}.json",
            self.output_dir / "runs" / run_id / "architecture" / architecture_version / "DBPack.json",
            self.output_dir / "runs" / run_id / "database" / architecture_version / f"DBPack_{architecture_version}.json",
            self.output_dir / "runs" / run_id / "database" / architecture_version / "DBPack.json",
        ]

        path = self._first_existing_path(possible_paths, "DBPack")
        return self._load_json_file(path, "DBPack"), path

    # ---------------------------------------------------------
    # Extraction helpers
    # ---------------------------------------------------------

    def _extract_project_name(self, srs_data: dict) -> str:
        """
        Extract project name from possible SRS shapes.
        """

        if srs_data.get("project_name"):
            return srs_data["project_name"]

        metadata = srs_data.get("metadata", {})
        if metadata.get("project_name"):
            return metadata["project_name"]

        return "Generated Application"

    def _extract_functional_requirements(self, srs_data: dict) -> list:
        """
        Extract functional requirements from possible SRS shapes.
        """

        if isinstance(srs_data.get("functional_requirements"), list):
            return srs_data["functional_requirements"]

        sections = srs_data.get("sections", {})
        if isinstance(sections.get("functional_requirements"), list):
            return sections["functional_requirements"]

        return []

    def _extract_db_entities(self, db_pack: dict) -> list[str]:
        """
        Extract entity names from DBPack for validation and traceability warnings.
        """

        if not isinstance(db_pack, dict):
            return []

        entities = (
            db_pack.get("entities")
            or db_pack.get("data_models")
            or db_pack.get("models")
            or []
        )

        entity_names = []

        for entity in entities:
            if isinstance(entity, dict):
                name = entity.get("name") or entity.get("entity_name")
                if name:
                    entity_names.append(name)

        return entity_names

    def _extract_endpoints_from_openapi(self, openapi_spec: str) -> list[str]:
        """
        Extract endpoint strings from OpenAPI text.
        """

        if not openapi_spec or not isinstance(openapi_spec, str):
            return []

        endpoints = []
        current_path = None

        for line in openapi_spec.splitlines():
            stripped = line.strip()

            path_match = re.match(r'^["\']?(/[^:"\']+)["\']?\s*:\s*$', stripped)
            if path_match:
                current_path = path_match.group(1)
                continue

            method_match = re.match(
                r"^(get|post|put|delete|patch)\s*:\s*$",
                stripped,
                re.IGNORECASE,
            )

            if current_path and method_match:
                method = method_match.group(1).upper()
                endpoints.append(f"{method} {current_path}")

        if not endpoints:
            paths = re.findall(r'["\']?(/[^"\':\s]+)["\']?\s*:', openapi_spec)
            endpoints = sorted(set(paths))

        return list(dict.fromkeys(endpoints))

    # ---------------------------------------------------------
    # File writing
    # ---------------------------------------------------------

    def _is_safe_path(self, relative_path: str) -> bool:
        """
        Call patch_policy.py.

        This supports both:
        - old function signature: is_safe_generated_path(path)
        - new function signature: is_safe_generated_path(path, tech_stack="mern")
        """

        try:
            return is_safe_generated_path(relative_path, tech_stack="mern")
        except TypeError:
            return is_safe_generated_path(relative_path)

    def _write_file(
        self,
        base_dir: Path,
        relative_path: str,
        content: str,
        purpose: str,
        owner_agent: str,
    ) -> GeneratedFile:
        """
        Write one generated file after path policy validation.
        """

        if not self._is_safe_path(relative_path):
            raise ValueError(f"Unsafe or unsupported MERN generated path: {relative_path}")

        file_path = base_dir / relative_path
        file_path.parent.mkdir(parents=True, exist_ok=True)

        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)

        return GeneratedFile(
            path=relative_path,
            purpose=purpose,
            owner_agent=owner_agent,
        )

    # ---------------------------------------------------------
    # Debug / repair helpers
    # ---------------------------------------------------------

    def _save_raw_llm_response(
        self,
        run_id: str,
        code_version: str,
        response_text: str,
        filename: str,
    ) -> str:
        """
        Save raw LLM responses for debugging.
        """

        debug_dir = (
            self.output_dir
            / "runs"
            / run_id
            / "code"
            / code_version
            / "debug"
        )

        debug_dir.mkdir(parents=True, exist_ok=True)

        debug_path = debug_dir / filename

        with open(debug_path, "w", encoding="utf-8") as f:
            f.write(response_text)

        return str(debug_path)

    async def _repair_llm_output_to_file_blocks(
        self,
        raw_text: str,
        step_name: str,
    ) -> str:
        """
        Repair formatting only.

        This does not generate new requirements.
        It asks the model to convert its previous response into file blocks.
        """

        repair_prompt = f"""
You generated code for the {step_name} step, but the output format was invalid.

Convert the previous response into ONLY valid AutoForge file blocks.

Required format:
<file path="relative/path/to/file.ext">
FULL FILE CONTENT HERE
</file>

Rules:
- Output ONLY file blocks.
- Your first character must be <.
- Do not explain anything.
- Do not use markdown headings.
- Do not use triple backticks.
- Do not add text before or after file blocks.
- Preserve the generated code content.
- Every file must have a relative path.
- Do not create placeholder files.
- Do not write TODO or "implement logic here".
- Use MERN stack files only.

Previous response:
{raw_text}
"""

        return await self.llm_provider.generate(repair_prompt)

    async def _generate_step_files(
        self,
        step_name: str,
        prompt: str,
        run_id: str,
        code_version: str,
    ) -> dict:
        """
        Generate files for one step:
        - Backend
        - Frontend
        - DevOps

        Each step gets:
        1. One generation call
        2. Parse attempt
        3. Repair call only if parse fails
        4. Debug files saved
        """

        response_text = await self.llm_provider.generate(prompt)

        self._save_raw_llm_response(
            run_id=run_id,
            code_version=code_version,
            response_text=response_text,
            filename=f"{step_name.lower()}_raw_response.txt",
        )

        try:
            return parse_file_plan(response_text)

        except CodeFileParseError:
            repaired_response = await self._repair_llm_output_to_file_blocks(
                raw_text=response_text,
                step_name=step_name,
            )

            self._save_raw_llm_response(
                run_id=run_id,
                code_version=code_version,
                response_text=repaired_response,
                filename=f"{step_name.lower()}_repaired_response.txt",
            )

            try:
                return parse_file_plan(repaired_response)

            except CodeFileParseError as repair_error:
                raise ValueError(
                    f"{step_name} generation failed. "
                    f"The LLM did not return valid file blocks even after repair. "
                    f"Parser error: {repair_error}"
                )

    # ---------------------------------------------------------
    # Ownership / responsibility
    # ---------------------------------------------------------

    def _owner_for_file(self, relative_path: str) -> str:
        """
        Assign generated files to internal responsibilities.
        """

        lower = relative_path.lower()

        if lower.startswith("backend/models/") or "model" in lower or "schema" in lower:
            return "Database Agent"

        if any(keyword in lower for keyword in [
            "docker",
            "compose",
            "readme",
            "package.json",
            "package-lock",
            "vite.config",
            ".gitignore",
            ".env.example",
        ]):
            return "DevOps Agent"

        return "Development Agent"

    def _responsibilities(self, generated_files: list[GeneratedFile]) -> list:
        """
        Build responsibility summary from generated file ownership.
        """

        development_outputs = []
        database_outputs = []
        devops_outputs = []

        for generated_file in generated_files:
            owner = self._owner_for_file(generated_file.path)

            if owner == "Development Agent":
                development_outputs.append(generated_file.path)
            elif owner == "Database Agent":
                database_outputs.append(generated_file.path)
            elif owner == "DevOps Agent":
                devops_outputs.append(generated_file.path)

        return [
            ResponsibilitySummary(
                agent_name="Development Agent",
                responsibility=(
                    "Generates Express backend logic, React frontend logic, "
                    "controllers, services, routes, and UI workflows from approved artifacts."
                ),
                outputs=development_outputs,
            ),
            ResponsibilitySummary(
                agent_name="Database Agent",
                responsibility=(
                    "Generates MongoDB/Mongoose data-layer implementation from DBPack "
                    "entities, fields, relationships, and constraints."
                ),
                outputs=database_outputs,
            ),
            ResponsibilitySummary(
                agent_name="DevOps Agent",
                responsibility=(
                    "Generates MERN dependency files, Docker Compose configuration, "
                    "environment examples, and README run instructions."
                ),
                outputs=devops_outputs,
            ),
        ]

    # ---------------------------------------------------------
    # Traceability
    # ---------------------------------------------------------

    def _traceability_links(
        self,
        functional_requirements: list,
        generated_files: list[GeneratedFile],
        openapi_spec: str,
    ) -> list:
        """
        Basic requirement-to-code traceability.

        Later this can be improved by matching requirement IDs to exact routes.
        """

        endpoints = self._extract_endpoints_from_openapi(openapi_spec)
        generated_paths = [file.path for file in generated_files]

        links = []

        for req in functional_requirements:
            req_id = req.get("id", "UNKNOWN")
            title = req.get("title", "Unknown Requirement")

            links.append(
                TraceabilityLink(
                    requirement_id=req_id,
                    requirement_title=title,
                    generated_files=generated_paths,
                    api_endpoints=endpoints,
                )
            )

        return links

    # ---------------------------------------------------------
    # Validation
    # ---------------------------------------------------------

    def _validate_generated_files_exist(self, code_files: dict) -> None:
        """
        Ensure at least some files were generated.
        """

        if not code_files:
            raise ValueError(
                "The LLM did not generate any files. "
                "No fallback application code will be created."
            )

    def _validate_required_mern_files(self, code_files: dict) -> None:
        """
        Validate the required MERN output.

        Because SDS may request monolith or microservices, backend internals may vary.
        But the minimum runnable MERN structure must still exist.
        """

        required_files = [
            "backend/package.json",
            "backend/server.js",
            "backend/config/db.js",
            "backend/models/index.js",
            "backend/routes/apiRoutes.js",
            "backend/controllers/apiController.js",
            "backend/services/businessService.js",
            "backend/.env.example",
            "frontend/package.json",
            "frontend/index.html",
            "frontend/vite.config.js",
            "frontend/src/main.jsx",
            "frontend/src/App.jsx",
            "frontend/src/api.js",
            "frontend/src/styles.css",
            "docker-compose.yml",
            ".gitignore",
            "README.md",
        ]

        missing_files = [
            file_path for file_path in required_files
            if file_path not in code_files
        ]

        if missing_files:
            raise ValueError(
                "Generated MERN app is incomplete. Missing required files: "
                + ", ".join(missing_files)
            )

    def _validate_no_placeholder_content(self, relative_path: str, content: str) -> None:
        """
        Reject clearly incomplete generated files.

        Important:
        We do NOT block the single word "placeholder" because valid code may use
        names like placeholderImage or comments like demo placeholder token.
        Instead, we block stronger incomplete-code phrases.
        """

        lower_content = content.lower()

        blocked_phrases = [
            "implement logic here",
            "implement logic for",
            "implement me",
            "generated endpoints should be implemented here",
            "generated content should go here",
            "add your code here",
            "write your code here",
            "replace this with",
            "this is a stub",
            "stub implementation",
            "not implemented",
            "coming soon",
            "... add more",
            "todo:",
            "fixme:",
            "xxx:",
            "hack:",
        ]

        for phrase in blocked_phrases:
            if phrase in lower_content:
                raise ValueError(
                    f"Generated file contains incomplete placeholder text: {relative_path}. "
                    f"Blocked phrase: {phrase}"
                )

        if len(content.strip()) < 5:
            raise ValueError(f"Generated file is empty or too short: {relative_path}")

    def _validate_openapi_coverage(self, code_files: dict, openapi_spec: str) -> list[str]:
        """
        Warning-only endpoint coverage check.
        """

        endpoints = self._extract_endpoints_from_openapi(openapi_spec)
        combined_code = "\n".join(code_files.values())
        warnings = []

        for endpoint in endpoints:
            if " " in endpoint:
                _, path = endpoint.split(" ", 1)
            else:
                path = endpoint

            if path not in combined_code:
                warnings.append(
                    f"API endpoint may be missing from generated code: {endpoint}"
                )

        return warnings

    def _validate_dbpack_usage(self, code_files: dict, db_pack: dict) -> list[str]:
        """
        Warning-only DBPack coverage check.
        """

        entities = self._extract_db_entities(db_pack)
        combined_code = "\n".join(code_files.values()).lower()
        warnings = []

        for entity in entities:
            entity_lower = entity.lower()
            plural_lower = f"{entity_lower}s"

            if entity_lower not in combined_code and plural_lower not in combined_code:
                warnings.append(
                    f"DBPack entity may be missing from generated code: {entity}"
                )

        return warnings

    # ---------------------------------------------------------
    # Main generation method
    # ---------------------------------------------------------

    async def generate_code(
        self,
        run_id: str,
        srs_version: str = "v1",
        code_version: str = "v1",
        domain_version: str = "v1",
        architecture_version: str = "v1",
    ) -> dict:
        """
        Generate runnable MERN application code from approved artifacts.

        This method uses split generation:
        1. Backend
        2. Frontend
        3. DevOps
        4. Integration and manifest
        """

        if not self.llm_provider:
            raise ValueError("llm_provider is required to generate code")

        # 1. Load upstream artifacts.
        srs_data, srs_path = self._load_srs(run_id, srs_version)
        domain_pack, domain_path = self._load_domain_pack(run_id, domain_version)
        sds_spec, sds_path = self._load_sds(run_id, architecture_version)
        openapi_spec, openapi_path = self._load_openapi(run_id, architecture_version)
        db_pack, db_path = self._load_db_pack(run_id, architecture_version)

        project_name = self._extract_project_name(srs_data)
        functional_reqs = self._extract_functional_requirements(srs_data)

        base_dir = (
            self.output_dir
            / "runs"
            / run_id
            / "code"
            / code_version
            / "generated_app"
        )

        # 2. Shared context used by all three prompts.
        context = {
            "project_name": project_name,
            "srs_data": srs_data,
            "domain_pack": domain_pack,
            "sds_spec": sds_spec,
            "openapi_spec": openapi_spec,
            "db_pack": db_pack,
        }

        # 3. Split generation steps.
        generation_steps = [
            ("Backend", build_backend_prompt(context)),
            ("Frontend", build_frontend_prompt(context)),
            ("DevOps", build_devops_prompt(context)),
        ]

        code_files = {}

        for step_name, prompt in generation_steps:
            step_files = await self._generate_step_files(
                step_name=step_name,
                prompt=prompt,
                run_id=run_id,
                code_version=code_version,
            )

            if not step_files:
                raise ValueError(f"{step_name} generation produced no files.")

            for rel_path, content in step_files.items():
                if rel_path in code_files:
                    raise ValueError(
                        f"Duplicate generated file path detected: {rel_path}"
                    )

                code_files[rel_path] = content

        # 4. Validate combined project output.
        self._validate_generated_files_exist(code_files)
        self._validate_required_mern_files(code_files)

        validation_warnings = []
        validation_warnings.extend(
            self._validate_openapi_coverage(code_files, openapi_spec)
        )
        validation_warnings.extend(
            self._validate_dbpack_usage(code_files, db_pack)
        )

        # 5. Write generated files.
        generated_files = []

        for rel_path, content in code_files.items():
            self._validate_no_placeholder_content(rel_path, content)

            generated_file = self._write_file(
                base_dir=base_dir,
                relative_path=rel_path,
                content=content,
                purpose=f"Generated from approved artifacts: {rel_path}",
                owner_agent=self._owner_for_file(rel_path),
            )

            generated_files.append(generated_file)

        # 6. Create manifest.
        manifest = CodeManifest(
            run_id=run_id,
            code_version=code_version,
            source_srs_version=srs_version,
            output_dir=str(base_dir),
            input_artifacts=[
                InputArtifactSummary(
                    artifact_name="SRS",
                    version=srs_version,
                    path=str(srs_path),
                ),
                InputArtifactSummary(
                    artifact_name="DomainPack",
                    version=domain_version,
                    path=str(domain_path),
                ),
                InputArtifactSummary(
                    artifact_name="SDS",
                    version=architecture_version,
                    path=str(sds_path),
                ),
                InputArtifactSummary(
                    artifact_name="OpenAPI",
                    version=architecture_version,
                    path=str(openapi_path),
                ),
                InputArtifactSummary(
                    artifact_name="DBPack",
                    version=architecture_version,
                    path=str(db_path),
                ),
            ],
            generated_files=generated_files,
            responsibilities=self._responsibilities(generated_files),
            traceability_links=self._traceability_links(
                functional_reqs,
                generated_files,
                openapi_spec,
            ),
            run_instructions=[
                "cd generated_app",
                "docker-compose up --build",
                "Or run backend and frontend manually using README.md.",
            ],
            validation_warnings=validation_warnings,
        )

        manifest_path = (
            self.output_dir
            / "runs"
            / run_id
            / "code"
            / code_version
            / f"CodeManifest_{code_version}.json"
        )

        manifest_path.parent.mkdir(parents=True, exist_ok=True)

        with open(manifest_path, "w", encoding="utf-8") as f:
            f.write(manifest.model_dump_json(indent=2))

        return {
            "status": "success",
            "run_id": run_id,
            "code_version": code_version,
            "source_srs_version": srs_version,
            "manifest_path": str(manifest_path),
            "output_dir": str(base_dir),
            "generated_file_count": len(generated_files),
            "input_artifacts": {
                "srs": str(srs_path),
                "domain_pack": str(domain_path),
                "sds": str(sds_path),
                "openapi": str(openapi_path),
                "db_pack": str(db_path),
            },
            "validation_warnings": validation_warnings,
        }