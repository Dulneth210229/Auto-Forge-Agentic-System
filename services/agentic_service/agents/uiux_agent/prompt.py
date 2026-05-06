import json
from agents.uiux_agent.schemas import UIScreen


def compact_openapi(api_contract: dict) -> list[dict]:
    """
    Converts OpenAPI into a compact endpoint list for the LLM.
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
        "domain_summary": (
            domain_pack.get("domain_summary")
            or domain_pack.get("summary")
            or domain_pack.get("overview")
        ),
        "business_entities": (
            domain_pack.get("business_entities", [])
            or domain_pack.get("entities", [])
        ),
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
        "architecture_style": (
            sds.get("architecture_style")
            or sds.get("style")
            or sds.get("architecture", {}).get("style")
        ),
        "modules": (
            sds.get("modules", [])
            or sds.get("system_modules", [])
            or sds.get("architecture", {}).get("modules", [])
        ),
        "api_endpoints": (
            sds.get("api_endpoints", [])
            or sds.get("endpoints", [])
        ),
        "data_entities": (
            db_pack.get("entities", [])
            or db_pack.get("tables", [])
            or db_pack.get("models", [])
        ),
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

    Important:
    This does NOT use a hardcoded screen list.
    The LLM must derive the UI/UX plan from approved upstream artifacts.
    """

    return f"""
Return ONLY valid JSON.

You are the UI/UX Agent in AutoForge, a governed SDLC automation system.

Generate the UI/UX plan from the approved SRS, DomainPack, Architecture, OpenAPI contract, and DBPack.

STRICT RULES:
- Return one JSON object only.
- Do not write markdown.
- Do not write explanation text.
- Do not include comments.
- Do not include component list diagrams.
- Do not hardcode a fixed screen list.
- Derive screens from approved artifacts.
- Create screens only for user-facing or admin-facing UI needs.
- Each screen must link to related FR IDs when possible.
- Use stable screen IDs: UI-SCR-01, UI-SCR-02, UI-SCR-03...
- Use stable flow node IDs: FLOW-N01, FLOW-N02, FLOW-N03...
- The user flow must include visible nodes and edges.
- Do not return empty nodes.
- Do not return empty edges.
- Include all major e-commerce screens required by the approved SRS and API contract.

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

UI/UX PLAN QUALITY RULES:
- The screen list must not be empty.
- The user flow nodes must not be empty.
- The user flow edges must not be empty.
- The first node must be "Start Journey".
- Every major screen must appear as a node in the user flow.
- Do NOT use generic labels like "Step 1", "Step 2", "Step 3".
- Do NOT use labels like "Screen", "Page", "Next", or "Action".
- Each flow node label must describe a real user action or screen purpose.
- Good labels: "Browse Product Catalog", "View Product Details", "Add Item to Cart", "Review Shopping Cart", "Enter Shipping Details", "Complete Payment", "View Order Confirmation".
- Edge conditions must explain the transition.
- Good edge labels: "Select product", "Click Add to Cart", "Proceed to Checkout", "Submit payment", "Order placed successfully".
- The flow should represent a realistic customer journey from entry to completion.
- If admin requirements exist, create a separate Admin Management Flow.
- Avoid backend-only modules as UI screens.

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
Your previous UI/UX plan output was invalid JSON or incomplete.

Parser error:
{error_message}

Previous invalid output:
{invalid_output}

Repair it into STRICT VALID JSON.

Rules:
- Return JSON only.
- Use double quotes for all property names.
- Use double quotes for all string values.
- Do not use comments.
- Do not use trailing commas.
- Do not use markdown.
- Do not write explanation text.
- Do not use Python dict syntax.
- Do not use JavaScript object syntax.
- Do not return empty screens.
- Do not return empty user flow nodes.
- Do not return empty user flow edges.

The JSON must contain exactly these top-level keys:
{{
  "screens": [],
  "user_flows": [],
  "traceability": []
}}

Required shape:
{{
  "screens": [
    {{
      "id": "UI-SCR-01",
      "name": "Screen Name",
      "file_name": "UI-SCR-01_screen_name.html",
      "description": "Screen description",
      "route": "/screen-route",
      "related_requirements": ["FR-001"]
    }}
  ],
  "user_flows": [
    {{
      "id": "UF-001",
      "name": "Main User Flow",
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
          "label": "Screen Name",
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
      "screen_name": "Screen Name",
      "reason": "This screen satisfies the requirement."
    }}
  ]
}}

Return only the corrected strict JSON now.
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

    Important:
    - No predefined UI templates are used.
    - The LLM generates the actual visual UI.
    - The backend only validates/repairs/wraps output.
    """

    related_frs = [
        fr for fr in srs.get("functional_requirements", [])
        if fr.get("id") in screen.related_requirements
    ]

    return f"""
You are the UI/UX Agent in AutoForge.

Generate ONE HIGH-FIDELITY wireframe as HTML + Tailwind CSS for the given screen.

STRICT OUTPUT RULES:
- Return ONLY HTML.
- Start with <!DOCTYPE html> or <main>.
- Do NOT include markdown fences.
- Do NOT include explanations.
- Do NOT include JSON.
- Do NOT include Mermaid.
- Do NOT include React.
- Do NOT use JavaScript.
- Do NOT use predefined templates.
- Do NOT create component list diagrams.
- Do NOT use external image URLs.
- Use Tailwind CSS CDN only.
- Generate the UI dynamically from the approved artifacts and the user prompt.
- The design must be detailed, polished, and suitable for a real product prototype.
- The result must be visually rich and should fill a 1366x768 screenshot.
- Avoid large blank areas.
- Avoid single-title pages.
- Avoid incomplete sections.
- Avoid incomplete table headers without rows.
- Avoid only placeholder boxes.
- The output must be more than 3500 characters of HTML.

MANDATORY DESIGN REQUIREMENTS:
- Include a clear top navigation or header.
- Include a clear page title and subtitle.
- Include at least 5 meaningful visual sections.
- Include realistic content, not only placeholders.
- Include realistic buttons, forms, cards, filters, summaries, tables, or side panels depending on screen purpose.
- Include spacing, rounded corners, shadows, borders, typography hierarchy.
- Use grid/flex layouts for structure.
- Include primary and secondary actions.
- Include realistic product/customer/order/cart related microcopy where relevant.
- Include helpful labels and screen-specific details.
- Include screen ID and related FR IDs in small visible text.
- Make the layout unique to this screen’s purpose.
- Use modern e-commerce SaaS styling.
- Use readable font sizes and professional spacing.
- Use status badges where relevant.
- Use product images as local placeholder panels only, not external URLs.
- Use color blocks, cards, icons with text characters, badges, and panels to improve visual clarity.
- Include footer/help/status area when relevant.

SCREEN-SPECIFIC EXPECTATIONS:
- Login/Register:
  Include authentication form, social login or support area, benefits side panel, validation/error examples, create account/forgot password links.
- Product Catalog:
  Include filters, search, category chips, product cards, pricing, ratings, stock badges, sorting, pagination or featured area.
- Product Details:
  Include gallery/preview area, product info, price, rating, specs, quantity selector, add-to-cart/buy-now buttons, delivery info, related products.
- Cart:
  Include item rows/cards, quantities, remove/save actions, totals, coupon area, checkout CTA.
- Checkout:
  Include customer info, shipping, payment, order summary, validation states, secure checkout notice.
- Order History:
  Include order cards/table, statuses, filters, order details, reorder/view actions.
- Admin:
  Include dashboard/table layout, filters, CRUD actions, status badges, analytics cards.

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
{user_prompt or "Generate a modern high-fidelity e-commerce wireframe with rich content and professional layout."}

Return ONLY the final HTML. Start directly with <!DOCTYPE html> or <main>.
""".strip()


def build_wireframe_repair_prompt(
    screen: UIScreen,
    invalid_output: str,
    error_message: str,
) -> str:
    """
    Repair prompt for invalid or weak HTML.
    """

    return f"""
Your previous wireframe HTML for {screen.id} - {screen.name} was invalid, incomplete, or too weak.

Error:
{error_message}

Previous invalid output:
{invalid_output}

Regenerate the wireframe from scratch.

STRICT RULES:
- Return ONLY HTML.
- Start with <!DOCTYPE html> or <main>.
- Do NOT include markdown.
- Do NOT include explanation text.
- Do NOT include JSON.
- Do NOT include Mermaid.
- Do NOT use JavaScript.
- Do NOT use React.
- Do NOT use predefined templates.
- Use Tailwind CSS CDN only.
- The output must be more than 3500 characters of HTML.

QUALITY REQUIREMENTS:
- Must be HIGH-FIDELITY, not low-fidelity.
- Must contain at least 5 meaningful visual sections.
- Must include navigation/header.
- Must include screen-specific content.
- Must include realistic labels, values, buttons, forms/cards/tables depending on the screen.
- Must avoid empty whitespace.
- Must avoid single-title pages.
- Must avoid incomplete table headers without rows.
- Must be suitable for 1366x768 rendering.
- Must use Tailwind classes heavily: grid, flex, rounded, shadow, spacing, borders, typography.
- Must include small text showing the screen ID and related FR IDs.
- Must look like a polished e-commerce web-app screen.

Return the corrected final HTML now.
""".strip()