import json
import os
from pathlib import Path

from openapi_spec_validator import validate_spec

from agents.architect_agent.schemas import (
    SDS,
    ArchitectureModule,
    ArchitectureResult,
)
from agents.architect_agent.openapi_builder import (
    build_default_api_endpoints,
    build_openapi_document,
    save_openapi_yaml,
)
from agents.architect_agent.db_pack_builder import build_db_pack
from agents.architect_agent.diagram_builder import (
    build_usecase_puml,
    build_class_puml,
    build_sequence_checkout_puml,
    build_sequence_order_history_puml,
    build_architecture_flow_puml,
)
from agents.architect_agent.visual_exporter import export_puml_to_png
from agents.architect_agent.renderer import (
    render_sds_markdown,
    render_db_pack_markdown,
)
from agents.architect_agent.traceability_builder import (
    build_architecture_traceability,
)


class ArchitectAgent:
    """
    Architect Agent for AutoForge.

    Inputs:
    - Approved SRS JSON
    - Approved DomainPack JSON

    Outputs:
    - SDS JSON + Markdown
    - OpenAPI YAML
    - DBPack JSON + Markdown
    - PlantUML diagrams (.puml)
    - PNG image diagrams
    - Architecture traceability JSON

    This version also supports revision:
    users can submit a change request and generate a new architecture version.
    """

    def __init__(self):
        self.output_dir = Path(os.getenv("OUTPUT_DIR", "outputs"))

    def generate_architecture(
        self,
        run_id: str,
        srs_version: str = "v1",
        domain_version: str = "v1",
        architecture_version: str = "v1",
        architecture_style: str = "modular_monolith",
        export_visuals: bool = True,
    ) -> ArchitectureResult:
        """
        Generates fresh architecture artifacts from SRS + DomainPack.
        """

        srs_path = (
            self.output_dir
            / "runs"
            / run_id
            / "srs"
            / srs_version
            / f"SRS_{srs_version}.json"
        )

        domain_path = (
            self.output_dir
            / "runs"
            / run_id
            / "domain"
            / domain_version
            / f"DomainPack_{domain_version}.json"
        )

        if not srs_path.exists():
            raise FileNotFoundError(f"SRS file not found: {srs_path}")

        if not domain_path.exists():
            raise FileNotFoundError(f"DomainPack file not found: {domain_path}")

        srs = json.loads(srs_path.read_text(encoding="utf-8"))
        domain_pack = json.loads(domain_path.read_text(encoding="utf-8"))

        return self._build_and_save_architecture(
            run_id=run_id,
            srs=srs,
            domain_pack=domain_pack,
            srs_version=srs_version,
            domain_version=domain_version,
            architecture_version=architecture_version,
            architecture_style=architecture_style,
            export_visuals=export_visuals,
        )

    def revise_architecture(
        self,
        run_id: str,
        current_version: str,
        new_version: str,
        change_request: str,
        export_visuals: bool = True,
    ) -> dict:
        """
        Revises an existing architecture version using user feedback.

        This method:
        1. Loads existing architecture artifacts
        2. Applies simple rule-based revision logic
        3. Generates new versioned outputs

        In later iterations this can be made more intelligent with an LLM.
        """

        base_path = self.output_dir / "runs" / run_id / "architecture" / current_version

        sds_path = base_path / f"SDS_{current_version}.json"
        db_pack_path = base_path / f"DBPack_{current_version}.json"

        if not sds_path.exists():
            raise FileNotFoundError(f"Existing SDS file not found: {sds_path}")

        if not db_pack_path.exists():
            raise FileNotFoundError(f"Existing DBPack file not found: {db_pack_path}")

        sds_data = json.loads(sds_path.read_text(encoding="utf-8"))
        db_pack_data = json.loads(db_pack_path.read_text(encoding="utf-8"))

        # -----------------------------
        # Apply simple revision logic
        # -----------------------------
        change_lower = change_request.lower()

        # Example: add product search support
        if "search" in change_lower:
            if not any(module["name"] == "Catalog Module" for module in sds_data["modules"]):
                pass

            api_paths = [api["path"] for api in sds_data["api_endpoints"]]

            if "/products/search" not in api_paths:
                sds_data["api_endpoints"].append({
                    "id": f"API-{len(sds_data['api_endpoints']) + 1:03d}",
                    "tag": "Catalog",
                    "method": "GET",
                    "path": "/products/search",
                    "summary": "Search products",
                    "description": "Searches products using keyword, category, and price range filters.",
                    "request_schema": None,
                    "response_schema": "ProductListResponse",
                    "related_requirements": ["FR-SEARCH"],
                })

        # Example: add Review entity
        if "review" in change_lower:
            entity_names = [entity["name"] for entity in db_pack_data["entities"]]

            if "Review" not in entity_names:
                db_pack_data["entities"].append({
                    "id": f"DE-{len(db_pack_data['entities']) + 1:03d}",
                    "name": "Review",
                    "description": "Represents product reviews submitted by customers.",
                    "attributes": [
                        {"name": "id", "type": "uuid", "required": True, "description": "Unique review ID."},
                        {"name": "user_id", "type": "uuid", "required": True, "description": "Reviewer user ID."},
                        {"name": "product_id", "type": "uuid", "required": True, "description": "Reviewed product ID."},
                        {"name": "rating", "type": "integer", "required": True, "description": "Rating score."},
                        {"name": "comment", "type": "text", "required": False, "description": "Review text."},
                    ],
                })

                db_pack_data["relationships"].append({
                    "source": "User",
                    "target": "Review",
                    "relationship": "1 to many",
                    "description": "One user can write many reviews.",
                })

                db_pack_data["relationships"].append({
                    "source": "Product",
                    "target": "Review",
                    "relationship": "1 to many",
                    "description": "One product can have many reviews.",
                })

        # Change architecture style if requested
        if "microservices" in change_lower:
            sds_data["architecture_style"] = "microservices"
            sds_data["overview"] = (
                "The system follows a microservices architecture. "
                "Core business capabilities are separated into independently deployable services."
            )

        if "modular monolith" in change_lower or "modular_monolith" in change_lower:
            sds_data["architecture_style"] = "modular_monolith"
            sds_data["overview"] = (
                "The system follows a modular monolith architecture. "
                "The application is deployed as one service with clearly separated internal modules."
            )

        # Use the revised JSON as input to rebuild final artifacts
        return self._build_and_save_architecture_from_existing(
            run_id=run_id,
            sds_data=sds_data,
            db_pack_data=db_pack_data,
            previous_version=current_version,
            architecture_version=new_version,
            export_visuals=export_visuals,
            change_request=change_request,
        )

    def _build_and_save_architecture(
        self,
        run_id: str,
        srs: dict,
        domain_pack: dict,
        srs_version: str,
        domain_version: str,
        architecture_version: str,
        architecture_style: str,
        export_visuals: bool,
    ) -> ArchitectureResult:
        """
        Internal builder for fresh architecture generation.
        """

        project_name = srs.get("project_name", "AutoForge E-commerce Platform")
        functional_requirements = srs.get("functional_requirements", [])

        architecture_dir = (
            self.output_dir
            / "runs"
            / run_id
            / "architecture"
            / architecture_version
        )

        diagrams_dir = architecture_dir / "diagrams"

        architecture_dir.mkdir(parents=True, exist_ok=True)
        diagrams_dir.mkdir(parents=True, exist_ok=True)

        api_endpoints = build_default_api_endpoints(functional_requirements)
        modules = self._build_modules(functional_requirements)

        sds = SDS(
            project_name=project_name,
            version=architecture_version,
            architecture_style=architecture_style,
            overview=(
                "The system follows a modular monolith architecture for the MVP. "
                "The application is deployed as one backend service, but internally "
                "separated into Identity, Catalog, Cart, Checkout, Order, and Admin modules."
            ),
            modules=modules,
            api_endpoints=api_endpoints,
            security_considerations=[
                "Use token-based authentication for protected endpoints.",
                "Hash user passwords before storage.",
                "Validate product stock before checkout.",
                "Prevent users from accessing other users' carts and orders.",
                "Use server-side validation for all request payloads.",
            ],
            deployment_assumptions=[
                "The MVP can run locally using FastAPI and a relational database.",
                "Docker support can be added later.",
                "Payment is mocked unless real payment integration is required.",
            ],
            technology_stack=[
                "Python FastAPI backend",
                "Relational database such as PostgreSQL or SQLite",
                "OpenAPI 3.0 for API contract",
                "PlantUML + Graphviz for diagrams",
                "Pydantic for validation",
            ],
        )

        db_pack = build_db_pack(
            project_name=project_name,
            version=architecture_version,
        )

        openapi_doc = build_openapi_document(
            project_name=project_name,
            api_endpoints=api_endpoints,
        )

        validate_spec(openapi_doc)

        return self._save_all_outputs(
            run_id=run_id,
            architecture_version=architecture_version,
            srs_version=srs_version,
            domain_version=domain_version,
            sds=sds,
            db_pack=db_pack,
            openapi_doc=openapi_doc,
            diagrams_dir=diagrams_dir,
            export_visuals=export_visuals,
            srs_for_traceability=srs,
        )

    def _build_and_save_architecture_from_existing(
        self,
        run_id: str,
        sds_data: dict,
        db_pack_data: dict,
        previous_version: str,
        architecture_version: str,
        export_visuals: bool,
        change_request: str,
    ) -> dict:
        """
        Rebuilds outputs from revised SDS/DBPack data.
        """

        architecture_dir = (
            self.output_dir
            / "runs"
            / run_id
            / "architecture"
            / architecture_version
        )

        diagrams_dir = architecture_dir / "diagrams"

        architecture_dir.mkdir(parents=True, exist_ok=True)
        diagrams_dir.mkdir(parents=True, exist_ok=True)

        sds_data["version"] = architecture_version
        db_pack_data["version"] = architecture_version

        sds = SDS.model_validate(sds_data)
        from agents.architect_agent.schemas import DBPack
        db_pack = DBPack.model_validate(db_pack_data)

        openapi_doc = build_openapi_document(
            project_name=sds.project_name,
            api_endpoints=sds.api_endpoints,
        )

        validate_spec(openapi_doc)

        traceability_links = []

        sds_json_path = architecture_dir / f"SDS_{architecture_version}.json"
        sds_md_path = architecture_dir / f"SDS_{architecture_version}.md"
        openapi_path = architecture_dir / f"OpenAPI_{architecture_version}.yaml"
        db_json_path = architecture_dir / f"DBPack_{architecture_version}.json"
        db_md_path = architecture_dir / f"DBPack_{architecture_version}.md"
        traceability_path = architecture_dir / f"Traceability_Architecture_{architecture_version}.json"

        sds_json_path.write_text(json.dumps(sds.model_dump(), indent=2), encoding="utf-8")
        sds_md_path.write_text(render_sds_markdown(sds), encoding="utf-8")
        save_openapi_yaml(openapi_doc, str(openapi_path))
        db_json_path.write_text(json.dumps(db_pack.model_dump(), indent=2), encoding="utf-8")
        db_md_path.write_text(render_db_pack_markdown(db_pack), encoding="utf-8")

        diagram_paths = self._generate_diagrams(
            diagrams_dir=diagrams_dir,
            architecture_version=architecture_version,
            db_pack=db_pack,
            api_endpoints=sds.api_endpoints,
            export_visuals=export_visuals,
        )

        traceability_path.write_text(json.dumps(traceability_links, indent=2), encoding="utf-8")

        return {
            "run_id": run_id,
            "previous_version": previous_version,
            "architecture_version": architecture_version,
            "change_request": change_request,
            "sds_path": str(sds_json_path),
            "sds_markdown_path": str(sds_md_path),
            "openapi_path": str(openapi_path),
            "db_pack_path": str(db_json_path),
            "db_pack_markdown_path": str(db_md_path),
            "traceability_path": str(traceability_path),
            "diagram_paths": diagram_paths,
        }

    def _save_all_outputs(
        self,
        run_id: str,
        architecture_version: str,
        srs_version: str,
        domain_version: str,
        sds,
        db_pack,
        openapi_doc,
        diagrams_dir: Path,
        export_visuals: bool,
        srs_for_traceability: dict,
    ) -> ArchitectureResult:
        """
        Saves all generated architecture artifacts.
        """

        architecture_dir = diagrams_dir.parent

        sds_json_path = architecture_dir / f"SDS_{architecture_version}.json"
        sds_md_path = architecture_dir / f"SDS_{architecture_version}.md"
        openapi_path = architecture_dir / f"OpenAPI_{architecture_version}.yaml"
        db_json_path = architecture_dir / f"DBPack_{architecture_version}.json"
        db_md_path = architecture_dir / f"DBPack_{architecture_version}.md"
        traceability_path = architecture_dir / f"Traceability_Architecture_{architecture_version}.json"

        sds_json_path.write_text(json.dumps(sds.model_dump(), indent=2), encoding="utf-8")
        sds_md_path.write_text(render_sds_markdown(sds), encoding="utf-8")
        save_openapi_yaml(openapi_doc, str(openapi_path))
        db_json_path.write_text(json.dumps(db_pack.model_dump(), indent=2), encoding="utf-8")
        db_md_path.write_text(render_db_pack_markdown(db_pack), encoding="utf-8")

        diagram_paths = self._generate_diagrams(
            diagrams_dir=diagrams_dir,
            architecture_version=architecture_version,
            db_pack=db_pack,
            api_endpoints=sds.api_endpoints,
            export_visuals=export_visuals,
        )

        traceability_links = build_architecture_traceability(
            srs=srs_for_traceability,
            sds=sds,
            db_pack=db_pack,
        )

        traceability_path.write_text(
            json.dumps([link.model_dump() for link in traceability_links], indent=2),
            encoding="utf-8",
        )

        return ArchitectureResult(
            run_id=run_id,
            architecture_version=architecture_version,
            srs_version=srs_version,
            domain_version=domain_version,
            sds_path=str(sds_json_path),
            sds_markdown_path=str(sds_md_path),
            openapi_path=str(openapi_path),
            db_pack_path=str(db_json_path),
            db_pack_markdown_path=str(db_md_path),
            traceability_path=str(traceability_path),
            diagram_paths=diagram_paths,
        )

    def _build_modules(self, functional_requirements: list[dict]) -> list[ArchitectureModule]:
        """
        Builds logical modules and links requirements using keyword matching.
        """

        def match_requirements(*keywords: str) -> list[str]:
            matched = []

            for fr in functional_requirements:
                text = f"{fr.get('title', '')} {fr.get('description', '')}".lower()

                if any(keyword.lower() in text for keyword in keywords):
                    matched.append(fr.get("id", ""))

            return matched or [fr.get("id", "") for fr in functional_requirements[:1]]

        return [
            ArchitectureModule(
                id="MOD-001",
                name="Identity Module",
                responsibility="Handles user registration, login, authentication, and role-based access.",
                related_requirements=match_requirements("user", "login", "register", "authentication"),
            ),
            ArchitectureModule(
                id="MOD-002",
                name="Catalog Module",
                responsibility="Handles product browsing, searching, filtering, and product details.",
                related_requirements=match_requirements("product", "catalog", "browse", "search"),
            ),
            ArchitectureModule(
                id="MOD-003",
                name="Cart Module",
                responsibility="Handles cart creation, adding items, updating quantities, and removing items.",
                related_requirements=match_requirements("cart"),
            ),
            ArchitectureModule(
                id="MOD-004",
                name="Checkout Module",
                responsibility="Validates cart, calculates totals, applies business rules, and prepares order creation.",
                related_requirements=match_requirements("checkout", "payment"),
            ),
            ArchitectureModule(
                id="MOD-005",
                name="Order Module",
                responsibility="Handles order placement, order status, and order history.",
                related_requirements=match_requirements("order", "history"),
            ),
            ArchitectureModule(
                id="MOD-006",
                name="Admin Module",
                responsibility="Handles basic product management for administrators.",
                related_requirements=match_requirements("admin", "manage products", "product management"),
            ),
        ]

    def _generate_diagrams(
        self,
        diagrams_dir: Path,
        architecture_version: str,
        db_pack,
        api_endpoints,
        export_visuals: bool,
    ) -> list[str]:
        """
        Generates PlantUML source files and PNG diagrams.
        """

        diagrams = {
            f"usecase_{architecture_version}.puml": build_usecase_puml(),
            f"class_{architecture_version}.puml": build_class_puml(db_pack),
            f"sequence_checkout_{architecture_version}.puml": build_sequence_checkout_puml(),
            f"sequence_order_history_{architecture_version}.puml": build_sequence_order_history_puml(),
            f"architecture_flow_{architecture_version}.puml": build_architecture_flow_puml(api_endpoints),
        }

        all_paths = []

        for filename, content in diagrams.items():
            puml_path = diagrams_dir / filename
            puml_path.write_text(content, encoding="utf-8")
            all_paths.append(str(puml_path))

            if export_visuals:
                exported = export_puml_to_png(puml_path)
                for path in exported:
                    if path not in all_paths:
                        all_paths.append(path)

        return all_paths