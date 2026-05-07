import json
import re

try:
    import yaml
except ImportError:
    yaml = None


# ---------------------------------------------------------
# Utility helpers
# ---------------------------------------------------------

def _to_text(value) -> str:
    """
    Convert dict/list/string values into readable prompt text.
    Used only when we need a fallback readable version.
    """

    if isinstance(value, (dict, list)):
        return json.dumps(value, indent=2)

    return str(value or "")


def _safe_list(value):
    """
    Normalize any value into a list.
    This prevents crashes when an artifact field is missing or has unexpected shape.
    """

    if isinstance(value, list):
        return value

    if value is None:
        return []

    return [value]


# ---------------------------------------------------------
# Artifact summarizers
# ---------------------------------------------------------

def _extract_openapi_endpoints(openapi_spec: str) -> str:
    """
    Extract endpoint paths and methods from OpenAPI YAML/JSON text.

    Priority:
    1. Use yaml.safe_load if PyYAML is installed.
    2. Fall back to regex if YAML parsing fails.
    """

    if not openapi_spec:
        return "- No OpenAPI spec provided"

    # Preferred parser: YAML/JSON parsing.
    if yaml:
        try:
            spec = yaml.safe_load(openapi_spec)

            if isinstance(spec, dict):
                paths = spec.get("paths", {})
                endpoints = []

                if isinstance(paths, dict):
                    for path, methods in paths.items():
                        if not isinstance(methods, dict):
                            continue

                        for method, details in methods.items():
                            if str(method).lower() in ["get", "post", "put", "delete", "patch"]:
                                summary = ""

                                if isinstance(details, dict):
                                    summary = (
                                        details.get("summary")
                                        or details.get("description")
                                        or ""
                                    )

                                if summary:
                                    endpoints.append(f"- {method.upper()} {path} — {summary}")
                                else:
                                    endpoints.append(f"- {method.upper()} {path}")

                if endpoints:
                    return "\n".join(sorted(set(endpoints)))

        except Exception:
            pass

    # Regex fallback for OpenAPI YAML text.
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
            endpoints.append(f"- {method_match.group(1).upper()} {current_path}")

    if endpoints:
        return "\n".join(sorted(set(endpoints)))

    paths = re.findall(r'["\']?(/[^"\':\s]+)["\']?\s*:', openapi_spec)
    if paths:
        return "\n".join([f"- {path}" for path in sorted(set(paths))])

    return "- Follow endpoints defined in the OpenAPI specification"


def _extract_sds_architecture(sds_spec: dict) -> str:
    """
    Extract architecture style from SDS.

    The Coder Agent does not decide monolith vs microservice itself.
    It reads the SDS and asks the LLM to follow that style.
    """

    if not isinstance(sds_spec, dict):
        return "Architecture style not provided. Use a clean modular MERN structure."

    possible_keys = [
        "architecture_style",
        "style",
        "system_architecture",
        "architecture",
        "deployment_style",
    ]

    for key in possible_keys:
        value = sds_spec.get(key)
        if value:
            return str(value)

    return "Architecture style not explicitly provided. Use modular MERN monolith unless SDS modules imply services."


def _extract_sds_modules(sds_spec: dict) -> str:
    """
    Extract module names and responsibilities from SDS.
    """

    if not isinstance(sds_spec, dict):
        return "- No SDS modules provided"

    modules = sds_spec.get("modules", [])

    if not modules:
        # Some SDS outputs may use another key.
        modules = sds_spec.get("components", [])

    if not modules:
        return "- No SDS modules provided"

    lines = []

    for module in modules:
        if isinstance(module, dict):
            name = module.get("name", "Module")
            responsibility = (
                module.get("responsibility")
                or module.get("description")
                or module.get("purpose")
                or ""
            )
            lines.append(f"- {name}: {responsibility}")

    return "\n".join(lines) if lines else "- No SDS modules provided"


def _extract_db_entities(db_pack: dict) -> str:
    """
    Extract entity names and fields from DBPack.
    """

    if not isinstance(db_pack, dict):
        return "- No database entities provided"

    entities = db_pack.get("entities", [])

    if not entities:
        entities = db_pack.get("data_models", [])

    if not entities:
        entities = db_pack.get("models", [])

    if not entities:
        return "- No database entities provided"

    lines = []

    for entity in entities:
        if not isinstance(entity, dict):
            continue

        name = entity.get("name") or entity.get("entity_name") or "Entity"
        fields = (
            entity.get("fields")
            or entity.get("attributes")
            or entity.get("properties")
            or []
        )

        field_parts = []

        if isinstance(fields, list):
            for field in fields:
                if isinstance(field, dict):
                    field_name = field.get("name") or field.get("field_name") or "field"
                    field_type = field.get("type") or field.get("data_type") or "String"
                    required = field.get("required", False)
                    required_text = " required" if required else ""
                    field_parts.append(f"{field_name}: {field_type}{required_text}")
                else:
                    field_parts.append(str(field))

        fields_text = ", ".join(field_parts) if field_parts else "fields from DBPack"
        lines.append(f"- {name}: {{{fields_text}}}")

    return "\n".join(lines) if lines else "- No database entities provided"


def _extract_srs_summary(srs_data: dict) -> str:
    """
    Create compact SRS summary.

    This avoids passing the full SRS JSON in every prompt.
    """

    if not isinstance(srs_data, dict):
        return "- No SRS data provided"

    lines = []

    project_name = (
        srs_data.get("project_name")
        or srs_data.get("metadata", {}).get("project_name")
    )

    if project_name:
        lines.append(f"- Project: {project_name}")

    scope = srs_data.get("scope")

    if isinstance(scope, str):
        lines.append(f"- Scope: {scope}")

    sections = srs_data.get("sections", {})

    functional_requirements = (
        srs_data.get("functional_requirements")
        or sections.get("functional_requirements")
        or []
    )

    if functional_requirements:
        lines.append("- Functional Requirements:")
        for req in functional_requirements[:25]:
            if isinstance(req, dict):
                req_id = req.get("id", "REQ")
                title = req.get("title", "")
                desc = req.get("description", "")
                lines.append(f"  - {req_id}: {title} — {desc}")
            else:
                lines.append(f"  - {req}")

    business_rules = (
        srs_data.get("business_rules")
        or sections.get("business_rules")
        or []
    )

    if business_rules:
        lines.append("- Business Rules:")
        for rule in business_rules[:15]:
            if isinstance(rule, dict):
                rule_id = rule.get("id", "BR")
                desc = rule.get("description") or rule.get("title") or ""
                lines.append(f"  - {rule_id}: {desc}")
            else:
                lines.append(f"  - {rule}")

    assumptions = srs_data.get("assumptions") or sections.get("assumptions") or []

    if assumptions:
        lines.append("- Assumptions:")
        for assumption in assumptions[:10]:
            lines.append(f"  - {assumption}")

    return "\n".join(lines) if lines else "- Use approved SRS for e-commerce requirements"


def _extract_domain_summary(domain_pack: dict) -> str:
    """
    Create compact DomainPack summary.
    """

    if not isinstance(domain_pack, dict):
        return "- No DomainPack provided"

    lines = []

    for key in ["domain_summary", "summary", "overview"]:
        if domain_pack.get(key):
            lines.append(f"- {key}: {domain_pack.get(key)}")

    workflows = (
        domain_pack.get("workflows")
        or domain_pack.get("domain_workflows")
        or []
    )

    if workflows:
        lines.append("- Domain Workflows:")
        for workflow in workflows[:12]:
            if isinstance(workflow, dict):
                name = workflow.get("name", "Workflow")
                desc = workflow.get("description", "")
                lines.append(f"  - {name}: {desc}")
            else:
                lines.append(f"  - {workflow}")

    rules = (
        domain_pack.get("business_rules")
        or domain_pack.get("rules")
        or []
    )

    if rules:
        lines.append("- Domain Rules:")
        for rule in rules[:12]:
            if isinstance(rule, dict):
                name = rule.get("name") or rule.get("id") or "Rule"
                desc = rule.get("description", "")
                lines.append(f"  - {name}: {desc}")
            else:
                lines.append(f"  - {rule}")

    return "\n".join(lines) if lines else "- Use DomainPack for e-commerce workflows and business behavior"


def _strict_file_block_rules() -> str:
    """
    Common output-format rules for all generation steps.
    """

    return """
STRICT OUTPUT RULES:
- Output ONLY <file path="...">...</file> blocks.
- Your first character must be <.
- Do not add explanations before or after file blocks.
- Do not use markdown headings outside file content.
- Do not wrap file content in triple backticks.
- Do not use [file path="..."] format.
- Do not output partial files.
- Do not output placeholder files.
- No TODO, FIXME, XXX, or empty functions.
- No Python, FastAPI, Flask, Django, Java, Spring Boot, PHP, Laravel, or non-MERN files.
"""


# ---------------------------------------------------------
# Split prompt builders
# ---------------------------------------------------------

def build_backend_prompt(context: dict) -> str:
    """
    Backend-only prompt.

    This generates Express/MongoDB backend files only.
    The backend architecture can be monolithic or service-oriented depending on SDS.
    """

    project_name = context.get("project_name", "AutoForge E-Commerce App")
    endpoint_summary = _extract_openapi_endpoints(context.get("openapi_spec", ""))
    module_summary = _extract_sds_modules(context.get("sds_spec", {}))
    architecture_style = _extract_sds_architecture(context.get("sds_spec", {}))
    entity_summary = _extract_db_entities(context.get("db_pack", {}))
    srs_summary = _extract_srs_summary(context.get("srs_data", {}))
    domain_summary = _extract_domain_summary(context.get("domain_pack", {}))

    return f"""You are an expert Node.js, Express.js, MongoDB, and Mongoose developer.

Generate ONLY backend files for a runnable MERN e-commerce app.

PROJECT:
{project_name}

AUTOFORGE STACK POLICY:
- Backend must use Node.js and Express.js.
- Database must use MongoDB with Mongoose.
- Backend must run on port 9000.
- Use dotenv and cors.
- Do not generate Python or Java files.

ARCHITECTURE STYLE FROM SDS:
{architecture_style}

IMPORTANT ARCHITECTURE RULE:
- If SDS indicates monolithic or modular-monolith, generate one Express backend under backend/.
- If SDS indicates microservices, generate a MERN-compatible service-oriented backend under backend/ with clear service folders.
- Even if microservices are used, ensure the generated backend has clear run instructions and docker-compose support.

SRS SUMMARY:
{srs_summary}

DOMAIN SUMMARY:
{domain_summary}

SDS MODULES:
{module_summary}

API ENDPOINTS TO IMPLEMENT:
{endpoint_summary}

DATABASE ENTITIES:
{entity_summary}

MINIMUM BACKEND FILES REQUIRED:
<file path="backend/package.json">...</file>
<file path="backend/server.js">...</file>
<file path="backend/config/db.js">...</file>
<file path="backend/models/index.js">...</file>
<file path="backend/routes/apiRoutes.js">...</file>
<file path="backend/controllers/apiController.js">...</file>
<file path="backend/services/businessService.js">...</file>
<file path="backend/.env.example">...</file>

You may add extra backend files if the SDS architecture needs them.

BACKEND REQUIREMENTS:
- backend/package.json must include express, mongoose, cors, dotenv, and nodemon.
- backend/server.js must connect routes, JSON middleware, CORS, MongoDB config, and listen on port 9000.
- backend/config/db.js must export MongoDB connection logic.
- backend/models/index.js must define Mongoose schemas for all DBPack entities.
- backend/routes/apiRoutes.js must define all OpenAPI routes.
- backend/controllers/apiController.js must implement controller functions for all routes.
- backend/services/businessService.js must contain reusable e-commerce business logic.
- Include realistic fallback/seed behavior if MongoDB is empty.
- Checkout/payment can be mocked unless artifacts require real integration.
- Do not leave endpoints empty.
- Do not return only placeholder responses.

{_strict_file_block_rules()}

Generate backend files now.
"""


def build_frontend_prompt(context: dict) -> str:
    """
    Frontend-only prompt.

    This generates React/Vite frontend files only.
    """

    project_name = context.get("project_name", "AutoForge E-Commerce App")
    endpoint_summary = _extract_openapi_endpoints(context.get("openapi_spec", ""))
    srs_summary = _extract_srs_summary(context.get("srs_data", {}))
    domain_summary = _extract_domain_summary(context.get("domain_pack", {}))

    return f"""You are an expert React and Vite frontend developer.

Generate ONLY frontend files for a runnable MERN e-commerce app.

PROJECT:
{project_name}

FRONTEND STACK:
- React
- Vite
- Plain CSS
- Backend API base URL: http://127.0.0.1:9000

SRS SUMMARY:
{srs_summary}

DOMAIN SUMMARY:
{domain_summary}

AVAILABLE API ENDPOINTS:
{endpoint_summary}

REQUIRED FRONTEND FILES:
<file path="frontend/package.json">...</file>
<file path="frontend/index.html">...</file>
<file path="frontend/vite.config.js">...</file>
<file path="frontend/src/main.jsx">...</file>
<file path="frontend/src/App.jsx">...</file>
<file path="frontend/src/api.js">...</file>
<file path="frontend/src/styles.css">...</file>

FRONTEND REQUIREMENTS:
- frontend/package.json must include react, react-dom, vite, and scripts.
- frontend/src/api.js must call http://127.0.0.1:9000.
- frontend/src/App.jsx must implement:
  - product catalog/browsing
  - product details where possible
  - shopping cart
  - checkout
  - order history
- Use API paths from the OpenAPI summary.
- Keep UI simple, clean, and usable.
- Use only React state/hooks and plain CSS.
- Do not generate TypeScript unless explicitly required; use JSX.

{_strict_file_block_rules()}

Generate frontend files now.
"""


def build_devops_prompt(context: dict) -> str:
    """
    DevOps-only prompt.

    This generates Docker Compose, README, and gitignore only.
    """

    project_name = context.get("project_name", "AutoForge E-Commerce App")
    architecture_style = _extract_sds_architecture(context.get("sds_spec", {}))

    return f"""You are a DevOps engineer.

Generate ONLY DevOps and project-level config files for a runnable MERN e-commerce app.

PROJECT:
{project_name}

ARCHITECTURE STYLE FROM SDS:
{architecture_style}

PORTS:
- Backend: 9000
- Frontend: 5173
- MongoDB: 27017

REQUIRED DEVOPS FILES:
<file path="docker-compose.yml">...</file>
<file path=".gitignore">...</file>
<file path="README.md">...</file>

DEVOPS REQUIREMENTS:
- docker-compose.yml must define backend, frontend, and mongodb services.
- If SDS indicates microservices, docker-compose.yml may include multiple backend services.
- Backend service must expose port 9000.
- Frontend service must expose port 5173.
- MongoDB service must expose port 27017.
- README.md must include:
  - generated project overview
  - prerequisites
  - how to run with docker-compose
  - how to run backend manually
  - how to run frontend manually
  - environment variable setup
  - useful URLs
- .gitignore must ignore node_modules, .env, dist, build, logs, and OS/editor files.

{_strict_file_block_rules()}

Generate DevOps files now.
"""


def build_coder_prompt(context: dict) -> str:
    """
    Backward-compatible wrapper.

    The new Coder Agent should call:
    - build_backend_prompt()
    - build_frontend_prompt()
    - build_devops_prompt()

    This wrapper remains only so older imports do not break.
    """

    return build_backend_prompt(context)

def build_revision_prompt(context: dict) -> str:
    """
    Build a focused revision prompt for existing generated code.

    This prompt does not regenerate the whole MERN project.
    It updates only the files provided in selected_files.
    """

    project_name = context.get("project_name", "AutoForge E-Commerce App")
    change_request = context.get("change_request", "")
    selected_files = context.get("selected_files", {})
    openapi_spec = context.get("openapi_spec", "")
    sds_spec = context.get("sds_spec", {})
    db_pack = context.get("db_pack", {})
    domain_pack = context.get("domain_pack", {})

    endpoint_summary = _extract_openapi_endpoints(openapi_spec)
    module_summary = _extract_sds_modules(sds_spec)
    entity_summary = _extract_db_entities(db_pack)
    domain_summary = _extract_domain_summary(domain_pack)

    selected_files_text = ""

    for path, content in selected_files.items():
        selected_files_text += f"\n\n--- FILE: {path} ---\n{content}\n"

    return f"""
You are the AutoForge Coder Agent revision worker.

Your task is to revise an existing MERN e-commerce generated app.

PROJECT:
{project_name}

USER CHANGE REQUEST:
{change_request}

STACK POLICY:
- Use MERN only.
- Backend: Node.js, Express.js, MongoDB, Mongoose.
- Frontend: React + Vite.
- Do not generate Python, Java, FastAPI, Spring Boot, Flask, Django, PHP, or Laravel files.

IMPORTANT:
- Do NOT regenerate the entire project.
- Revise only the affected files.
- Preserve existing file paths.
- Return full updated file content for each changed file.
- Do not return unchanged files unless needed.

OPENAPI ENDPOINTS:
{endpoint_summary}

SDS MODULES:
{module_summary}

DBPACK ENTITIES:
{entity_summary}

DOMAIN SUMMARY:
{domain_summary}

SELECTED EXISTING FILES:
{selected_files_text}

OUTPUT FORMAT:
Output ONLY file blocks.
Your first character in the response must be < and your response must start with <file path="...">.

Use this exact format:

<file path="relative/path/to/file.ext">
FULL UPDATED FILE CONTENT HERE
</file>

RULES:
- No markdown outside file blocks.
- No explanations.
- No TODO, FIXME, placeholder, or incomplete code.
- Every returned file must be complete and runnable.
- Keep MERN structure.
- If modifying routes, also update matching controller/service code when needed.
- If modifying frontend API calls, make sure they match backend routes.
"""