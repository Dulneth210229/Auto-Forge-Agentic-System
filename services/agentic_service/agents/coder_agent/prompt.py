import json
import re

try:
    import yaml
except ImportError:
    yaml = None


def _to_text(value) -> str:
    """
    Convert dict/list/string values into readable prompt text.
    """
    if isinstance(value, (dict, list)):
        return json.dumps(value, indent=2)
    return str(value or "")


def _extract_openapi_endpoints(openapi_spec: str) -> str:
    """
    Extract endpoint paths and methods from OpenAPI YAML/JSON text.
    Uses YAML parsing when available, then regex fallback.
    """

    if not openapi_spec:
        return "- No OpenAPI spec provided"

    if yaml:
        try:
            spec = yaml.safe_load(openapi_spec)
            paths = spec.get("paths", {}) if isinstance(spec, dict) else {}

            endpoints = []

            for path, methods in paths.items():
                if isinstance(methods, dict):
                    for method, details in methods.items():
                        if method.lower() in ["get", "post", "put", "delete", "patch"]:
                            summary = ""
                            if isinstance(details, dict):
                                summary = details.get("summary", "") or details.get("description", "")
                            if summary:
                                endpoints.append(f"- {method.upper()} {path} — {summary}")
                            else:
                                endpoints.append(f"- {method.upper()} {path}")

            if endpoints:
                return "\n".join(sorted(set(endpoints)))

        except Exception:
            pass

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


def _extract_sds_modules(sds_spec: dict) -> str:
    """
    Extract module names and responsibilities from SDS.
    """

    if not isinstance(sds_spec, dict):
        return "- No SDS modules provided"

    modules = sds_spec.get("modules", [])

    if not modules:
        return "- No SDS modules provided"

    lines = []

    for module in modules:
        if isinstance(module, dict):
            name = module.get("name", "Module")
            responsibility = module.get("responsibility", "")
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
        return "- No database entities provided"

    lines = []

    for entity in entities:
        if not isinstance(entity, dict):
            continue

        name = entity.get("name", "Entity")
        fields = entity.get("fields", [])

        field_parts = []

        if isinstance(fields, list):
            for field in fields:
                if isinstance(field, dict):
                    field_name = field.get("name", "field")
                    field_type = field.get("type", "String")
                    required = field.get("required", False)
                    required_text = " required" if required else ""
                    field_parts.append(f"{field_name}: {field_type}{required_text}")

        fields_text = ", ".join(field_parts) if field_parts else "fields from DBPack"
        lines.append(f"- {name}: {{{fields_text}}}")

    return "\n".join(lines) if lines else "- No database entities provided"


def _extract_srs_summary(srs_data: dict) -> str:
    """
    Create a short SRS summary instead of passing the full SRS JSON.
    """

    if not isinstance(srs_data, dict):
        return "- No SRS data provided"

    lines = []

    project_name = srs_data.get("project_name") or srs_data.get("metadata", {}).get("project_name")
    if project_name:
        lines.append(f"- Project: {project_name}")

    scope = srs_data.get("scope")
    if scope:
        lines.append(f"- Scope: {scope}")

    sections = srs_data.get("sections", {})

    functional_requirements = (
        srs_data.get("functional_requirements")
        or sections.get("functional_requirements")
        or []
    )

    if functional_requirements:
        lines.append("- Functional Requirements:")
        for req in functional_requirements[:20]:
            if isinstance(req, dict):
                req_id = req.get("id", "REQ")
                title = req.get("title", "")
                desc = req.get("description", "")
                lines.append(f"  - {req_id}: {title} — {desc}")

    business_rules = srs_data.get("business_rules") or sections.get("business_rules") or []
    if business_rules:
        lines.append("- Business Rules:")
        for rule in business_rules[:15]:
            if isinstance(rule, dict):
                lines.append(f"  - {rule.get('id', 'BR')}: {rule.get('description', rule.get('title', ''))}")
            else:
                lines.append(f"  - {rule}")

    return "\n".join(lines) if lines else "- Use the approved SRS for e-commerce requirements"


def _extract_domain_summary(domain_pack: dict) -> str:
    """
    Create a compact DomainPack summary.
    """

    if not isinstance(domain_pack, dict):
        return "- No DomainPack provided"

    lines = []

    for key in ["domain_summary", "summary", "overview"]:
        if domain_pack.get(key):
            lines.append(f"- {key}: {domain_pack.get(key)}")

    workflows = domain_pack.get("workflows") or domain_pack.get("domain_workflows") or []
    if workflows:
        lines.append("- Domain Workflows:")
        for workflow in workflows[:10]:
            if isinstance(workflow, dict):
                lines.append(f"  - {workflow.get('name', 'Workflow')}: {workflow.get('description', '')}")
            else:
                lines.append(f"  - {workflow}")

    rules = domain_pack.get("business_rules") or domain_pack.get("rules") or []
    if rules:
        lines.append("- Domain Rules:")
        for rule in rules[:10]:
            if isinstance(rule, dict):
                lines.append(f"  - {rule.get('name', rule.get('id', 'Rule'))}: {rule.get('description', '')}")
            else:
                lines.append(f"  - {rule}")

    return "\n".join(lines) if lines else "- Use DomainPack for e-commerce workflows and business behavior"


def _strict_file_block_rules() -> str:
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


def build_backend_prompt(context: dict) -> str:
    """
    Generate only MERN backend files.
    """

    project_name = context.get("project_name", "AutoForge E-Commerce App")
    endpoint_summary = _extract_openapi_endpoints(context.get("openapi_spec", ""))
    module_summary = _extract_sds_modules(context.get("sds_spec", {}))
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

Generate these exact backend files with FULL working code:

<file path="backend/package.json">
...
</file>

<file path="backend/server.js">
...
</file>

<file path="backend/config/db.js">
...
</file>

<file path="backend/models/index.js">
...
</file>

<file path="backend/routes/apiRoutes.js">
...
</file>

<file path="backend/controllers/apiController.js">
...
</file>

<file path="backend/services/businessService.js">
...
</file>

<file path="backend/.env.example">
...
</file>

BACKEND REQUIREMENTS:
- backend/package.json must include express, mongoose, cors, dotenv, nodemon.
- backend/server.js must connect routes, JSON middleware, CORS, and MongoDB config.
- backend/config/db.js must export MongoDB connection logic.
- backend/models/index.js must define Mongoose schemas for all DBPack entities.
- backend/routes/apiRoutes.js must define all OpenAPI routes.
- backend/controllers/apiController.js must implement controller functions for all routes.
- backend/services/businessService.js must contain reusable e-commerce business logic.
- Include realistic in-code fallback/seed data if MongoDB is empty.
- Checkout/payment can be mocked unless artifacts require real payment integration.
- Do not leave endpoints empty.
- Do not return only placeholder responses.

{_strict_file_block_rules()}

Generate backend files now.
"""


def build_frontend_prompt(context: dict) -> str:
    """
    Generate only React/Vite frontend files.
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

Generate these exact frontend files with FULL working code:

<file path="frontend/package.json">
...
</file>

<file path="frontend/index.html">
...
</file>

<file path="frontend/vite.config.js">
...
</file>

<file path="frontend/src/main.jsx">
...
</file>

<file path="frontend/src/App.jsx">
...
</file>

<file path="frontend/src/api.js">
...
</file>

<file path="frontend/src/styles.css">
...
</file>

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
- Do not generate TypeScript unless required by prompt; use JSX.

{_strict_file_block_rules()}

Generate frontend files now.
"""


def build_devops_prompt(context: dict) -> str:
    """
    Generate only DevOps/config files.
    """

    project_name = context.get("project_name", "AutoForge E-Commerce App")

    return f"""You are a DevOps engineer.

Generate ONLY DevOps and project-level config files for a runnable MERN e-commerce app.

PROJECT:
{project_name}

PORTS:
- Backend: 9000
- Frontend: 5173
- MongoDB: 27017

Generate these exact files with FULL working content:

<file path="docker-compose.yml">
...
</file>

<file path=".gitignore">
...
</file>

<file path="README.md">
...
</file>

DEVOPS REQUIREMENTS:
- docker-compose.yml must define backend, frontend, and mongodb services.
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
    Prefer using build_backend_prompt, build_frontend_prompt, and build_devops_prompt.
    """

    return build_backend_prompt(context)