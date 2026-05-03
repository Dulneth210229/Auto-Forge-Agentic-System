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
    build_use_case_diagram,
    build_class_diagram,
    build_checkout_sequence_diagram,
    build_order_history_sequence_diagram,
    build_architecture_flow_diagram,
)
from agents.architect_agent.visual_exporter import export_mermaid_to_visuals
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

    This agent receives:
    - Approved SRS JSON
    - Approved DomainPack JSON

    It generates:
    - SDS JSON + Markdown
    - OpenAPI YAML
    - DBPack JSON + Markdown
    - Mermaid diagrams
    - Optional PNG/PDF/JPG visuals from Mermaid
    - Architecture traceability links

    Design principle:
    We avoid fully uncontrolled LLM generation in this MVP.
    Instead, we use deterministic builders for stable, valid artifacts.
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
        Main Architect Agent workflow.

        Steps:
        1. Load SRS
        2. Load DomainPack
        3. Build logical modules
        4. Build API endpoints
        5. Build SDS
        6. Build OpenAPI YAML
        7. Build DBPack
        8. Build diagrams
        9. Export diagrams as PNG/PDF/JPG if possible
        10. Build traceability
        11. Save all artifacts
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
                "separated into Identity, Catalog, Cart, Checkout, Order, and Admin modules. "
                "This keeps development simple while preserving clear boundaries for future scaling."
            ),
            modules=modules,
            api_endpoints=api_endpoints,
            security_considerations=[
                "Use token-based authentication for protected endpoints.",
                "Hash user passwords before storage.",
                "Validate product stock before checkout.",
                "Prevent users from accessing other users' carts and orders.",
                "Use server-side validation for all request payloads.",
                "Log security-relevant events such as failed login attempts.",
            ],
            deployment_assumptions=[
                "The MVP can run locally using FastAPI and a relational database.",
                "Docker support can be added by the Coder or DevOps Agent.",
                "Payment is mocked unless real payment gateway integration is explicitly required.",
            ],
            technology_stack=[
                "Python FastAPI backend",
                "Relational database such as PostgreSQL or SQLite for MVP",
                "OpenAPI 3.0 for API contract",
                "Mermaid for architecture and UML-style diagrams",
                "Pydantic for schema validation",
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

        # Validate OpenAPI before saving. If invalid, this raises an error early.
        validate_spec(openapi_doc)

        sds_json_path = architecture_dir / f"SDS_{architecture_version}.json"
        sds_md_path = architecture_dir / f"SDS_{architecture_version}.md"
        openapi_path = architecture_dir / f"OpenAPI_{architecture_version}.yaml"
        db_json_path = architecture_dir / f"DBPack_{architecture_version}.json"
        db_md_path = architecture_dir / f"DBPack_{architecture_version}.md"
        traceability_path = architecture_dir / f"Traceability_Architecture_{architecture_version}.json"

        sds_json_path.write_text(
            json.dumps(sds.model_dump(), indent=2),
            encoding="utf-8",
        )

        sds_md_path.write_text(
            render_sds_markdown(sds),
            encoding="utf-8",
        )

        save_openapi_yaml(openapi_doc, str(openapi_path))

        db_json_path.write_text(
            json.dumps(db_pack.model_dump(), indent=2),
            encoding="utf-8",
        )

        db_md_path.write_text(
            render_db_pack_markdown(db_pack),
            encoding="utf-8",
        )

        diagram_paths = self._generate_diagrams(
            diagrams_dir=diagrams_dir,
            architecture_version=architecture_version,
            db_pack=db_pack,
            api_endpoints=api_endpoints,
            export_visuals=export_visuals,
        )

        traceability_links = build_architecture_traceability(
            srs=srs,
            sds=sds,
            db_pack=db_pack,
        )

        traceability_path.write_text(
            json.dumps(
                [link.model_dump() for link in traceability_links],
                indent=2,
            ),
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

            # Return at least one FR if available, so traceability is never empty.
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
        Generates Mermaid diagram files and optionally exports visuals.

        Visual exports:
        - PNG
        - PDF
        - JPG

        Mermaid source files are always created.
        """

        diagrams = {
            f"use_case_diagram_{architecture_version}.mmd": build_use_case_diagram(),
            f"class_diagram_{architecture_version}.mmd": build_class_diagram(db_pack),
            f"sequence_checkout_{architecture_version}.mmd": build_checkout_sequence_diagram(),
            f"sequence_order_history_{architecture_version}.mmd": build_order_history_sequence_diagram(),
            f"architecture_flow_{architecture_version}.mmd": build_architecture_flow_diagram(api_endpoints),
        }

        all_paths = []

        for filename, content in diagrams.items():
            mmd_path = diagrams_dir / filename
            mmd_path.write_text(content, encoding="utf-8")
            all_paths.append(str(mmd_path))

            if export_visuals:
                exported = export_mermaid_to_visuals(mmd_path)
                for path in exported:
                    if path not in all_paths:
                        all_paths.append(path)

        return all_paths