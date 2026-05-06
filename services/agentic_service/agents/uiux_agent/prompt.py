import json
from agents.uiux_agent.schemas import UIScreen


def compact_openapi(api_contract: dict) -> list[dict]:
    """
    Converts OpenAPI into compact endpoint list for the LLM.
    Full OpenAPI can be too large for local Ollama models.
    """

    compact = []

    for path, methods in api_contract.get("paths", {}).items():
        if not isinstance(methods, dict):
            continue

        for method, operation in methods.items():
            if method.lower() not in ["get", "post", "put", "patch", "delete"]:
                continue

            if not isinstance(operation, dict):
                continue

            compact.append({
                "method": method.upper(),
                "path": path,
                "tags": operation.get("tags", []),
                "summary": operation.get("summary", ""),
                "description": operation.get("description", ""),
            })

    return compact


def compact_srs(srs: dict) -> dict:
    """
    Keeps only UI/UX-relevant SRS fields.
    """

    return {
        "project_name": srs.get("project_name"),
        "roles": srs.get("roles", []),
        "functional_requirements": srs.get("functional_requirements", []),
        "non_functional_requirements": srs.get("non_functional_requirements", []),
        "workflows": srs.get("workflows", []),
        "business_rules": srs.get("business_rules", []),
        "constraints": srs.get("constraints", []),
        "assumptions": srs.get("assumptions", []),
    }


def compact_domain_pack(domain_pack: dict) -> dict:
    """
    Keeps only useful DomainPack data for UI/UX.
    Different DomainPack versions may use different keys, so we keep it flexible.
    """

    return {
        "project_name": domain_pack.get("project_name"),
        "version": domain_pack.get("version"),
        "domain_summary": domain_pack.get("domain_summary")
        or domain_pack.get("summary")
        or domain_pack.get("overview"),
        "business_entities": domain_pack.get("business_entities", [])
        or domain_pack.get("entities", []),
        "business_rules": domain_pack.get("business_rules", []),
        "workflows": domain_pack.get("workflows", []),
        "constraints": domain_pack.get("constraints", []),
    }


def compact_architecture(sds: dict, db_pack: dict) -> dict:
    """
    Keeps architecture details useful for UI/UX.
    Diagrams are excluded.
    """

    return {
        "architecture_style": sds.get("architecture_style")
        or sds.get("style")
        or sds.get("architecture", {}).get("style"),
        "modules": sds.get("modules", [])
        or sds.get("system_modules", [])
        or sds.get("architecture", {}).get("modules", []),
        "api_endpoints": sds.get("api_endpoints", [])
        or sds.get("endpoints", []),
        "data_entities": db_pack.get("entities", [])
        or db_pack.get("tables", [])
        or db_pack.get("models", []),
        "relationships": db_pack.get("relationships", []),
    }


def build_uiux_plan_prompt(
    project_name: str,
    srs: dict,
    domain_pack: dict,
    sds: dict,
    api_contract: dict,
    db_pack: dict,
    uiux_version: str,
    user_prompt: str | None = None,
) -> str:
    """
    LLM prompt for generating:
    - UI screens
    - user flows
    - traceability

    No hardcoded UI list is used.
    """

    return f"""
Return ONLY valid JSON.

You are the UI/UX Agent in AutoForge.

Generate the UI/UX plan from the approved SRS, DomainPack, Architecture, OpenAPI contract, and DBPack.

STRICT RULES:
- Return one JSON object only.
- Do not write markdown.
- Do not write explanation text.
- Do not include component list diagrams.
- Do not hardcode a fixed screen list.
- Derive screens from approved artifacts.
- Use stable screen IDs: UI-SCR-01, UI-SCR-02, UI-SCR-03...
- Use stable flow node IDs: FLOW-N01, FLOW-N02, FLOW-N03...
- Create screens only for user-facing or admin-facing UI needs.
- Each screen should link to related FR IDs when possible.

Your JSON MUST contain exactly these top-level keys:
- screens
- user_flows
- traceability

Required JSON shape:
{{
  "screens": [
    {{
      "id": "UI-SCR-01",
      "name": "Product Catalog",
      "file_name": "UI-SCR-01_product_catalog.html",
      "description": "High-fidelity product browsing screen.",
      "route": "/products",
      "related_requirements": ["FR-001"]
    }}
  ],
  "user_flows": [
    {{
      "id": "UF-001",
      "name": "Main Customer Flow",
      "actor": "Customer",
      "nodes": [
        {{
          "id": "FLOW-N01",
          "label": "Start",
          "screen_id": null,
          "related_requirements": []
        }},
        {{
          "id": "FLOW-N02",
          "label": "Product Catalog",
          "screen_id": "UI-SCR-01",
          "related_requirements": ["FR-001"]
        }}
      ],
      "edges": [
        {{
          "from_node": "FLOW-N01",
          "to_node": "FLOW-N02",
          "condition": "Start journey"
        }}
      ]
    }}
  ],
  "traceability": [
    {{
      "requirement_id": "FR-001",
      "screen_id": "UI-SCR-01",
      "screen_name": "Product Catalog",
      "reason": "This screen supports product browsing."
    }}
  ]
}}

Project name:
{project_name}

UI/UX version:
{uiux_version}

Approved SRS:
{json.dumps(compact_srs(srs), indent=2)}

Approved DomainPack:
{json.dumps(compact_domain_pack(domain_pack), indent=2)}

Approved Architecture excluding diagrams:
{json.dumps(compact_architecture(sds, db_pack), indent=2)}

Approved API Contract:
{json.dumps(compact_openapi(api_contract), indent=2)}

User prompt / change request:
{user_prompt or "None"}

Now return ONLY valid JSON.
""".strip()


def build_uiux_plan_repair_prompt(
    invalid_output: str,
    error_message: str,
) -> str:
    """
    If the LLM returns wrong JSON format, ask it to repair.
    """

    return f"""
Your previous UI/UX plan JSON was invalid.

Parser error:
{error_message}

Previous invalid output:
{invalid_output}

Repair it.

Return ONLY valid JSON with exactly these top-level keys:
- screens
- user_flows
- traceability

Do not write markdown.
Do not write explanation text.

Return corrected JSON now.
""".strip()


def build_high_fidelity_wireframe_prompt(
    project_name: str,
    screen: UIScreen,
    srs: dict,
    domain_pack: dict,
    sds: dict,
    api_contract: dict,
    db_pack: dict,
    all_screens: list[dict],
    user_prompt: str | None = None,
) -> str:
    """
    LLM prompt for one high-fidelity HTML wireframe.
    """

    related_frs = [
        fr for fr in srs.get("functional_requirements", [])
        if fr.get("id") in screen.related_requirements
    ]

    return f"""
You are the UI/UX Agent in AutoForge.

Generate ONE high-fidelity HTML + Tailwind CSS wireframe for the given screen.

STRICT OUTPUT RULES:
- - Return ONLY HTML. A complete HTML document is preferred, but a <main>...</main> layout is also acceptable.
- Start with <!DOCTYPE html>.
- End with </html>.
- Do not include markdown fences.
- Do not include explanations.
- Do not include JSON.
- Do not include Mermaid.
- Do not include React.
- Do not use JavaScript.
- Do not use external image URLs.
- Use Tailwind CSS CDN only.
- Do not use predefined templates.
- Do not create component list diagrams.
- Generate the UI dynamically from approved artifacts and the user prompt.
- Make it high-fidelity, visually rich, and human-understandable.
- Fit a 1366x768 screenshot.
- Include screen ID and related FR IDs in small visible text.

Required skeleton:
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>{screen.id} - {screen.name}</title>
    <script src="https://cdn.tailwindcss.com"></script>
</head>
<body>
</body>
</html>

Project name:
{project_name}

Current screen:
{json.dumps(screen.model_dump(), indent=2)}

All UI screens:
{json.dumps(all_screens, indent=2)}

Related functional requirements:
{json.dumps(related_frs, indent=2)}

Approved SRS:
{json.dumps(compact_srs(srs), indent=2)}

Approved DomainPack:
{json.dumps(compact_domain_pack(domain_pack), indent=2)}

Approved Architecture excluding diagrams:
{json.dumps(compact_architecture(sds, db_pack), indent=2)}

Approved API contract:
{json.dumps(compact_openapi(api_contract), indent=2)}

User wireframe prompt:
{user_prompt or "Generate a modern high-fidelity e-commerce UI/UX wireframe that matches the approved artifacts."}

Design quality:
- Modern e-commerce SaaS style.
- Rich navigation.
- Clear visual hierarchy.
- Proper forms, cards, summaries, filters, tables, status blocks where relevant.
- Realistic labels and microcopy.
- Primary and secondary actions.
- Empty/error/success states where relevant.
- Unique layout for this screen purpose.

Return ONLY the final HTML. Start directly with <!DOCTYPE html> or <main>.
""".strip()


def build_wireframe_repair_prompt(
    screen: UIScreen,
    invalid_output: str,
    error_message: str,
) -> str:
    """
    Repair prompt for invalid HTML.
    """

    return f"""
Your previous HTML output for {screen.id} - {screen.name} was invalid.

Parser error:
{error_message}

Previous invalid output:
{invalid_output}

Repair the output.

Return ONLY complete HTML.
Start with <!DOCTYPE html>.
End with </html>.
Use Tailwind CSS CDN:
<script src="https://cdn.tailwindcss.com"></script>

Do not write explanations.
Do not write markdown.
Do not write JSON.
Do not write text outside HTML.

Return corrected complete HTML now.
""".strip()