import json
from agents.uiux_agent.schemas import UIScreen


def build_uiux_plan_prompt(
    project_name: str,
    srs: dict,
    api_contract: dict,
    uiux_version: str,
    change_request: str | None = None,
) -> str:
    """
    Builds the LLM prompt that generates:
    - UI screens
    - user flows
    - FR-to-UI traceability

    The output must be JSON only.
    """

    return f"""
You are the UI/UX Agent inside AutoForge.

AutoForge is a governed SDLC automation platform.
Your job is to generate the UI/UX design plan from the APPROVED SRS and APPROVED API CONTRACT.

CRITICAL RULES:
- Return ONLY valid JSON.
- Do NOT include markdown.
- Do NOT include explanations.
- Do NOT include comments.
- Do NOT hardcode a fixed e-commerce screen list.
- Derive screens from the approved SRS and approved API contract.
- Generate only screens that are justified by requirements or API endpoints.
- Use stable screen IDs: UI-SCR-01, UI-SCR-02, UI-SCR-03...
- Use stable flow node IDs: FLOW-N01, FLOW-N02, FLOW-N03...
- Use stable flow ID: UF-001.
- Do NOT include component list diagram outputs.

You must produce this exact JSON structure:

{{
  "screens": [
    {{
      "id": "UI-SCR-01",
      "name": "Screen Name",
      "file_name": "UI-SCR-01_screen_name.html",
      "description": "What this screen is for",
      "route": "/route-name",
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
      "reason": "Explain why this screen satisfies the requirement"
    }}
  ]
}}

Approved SRS:
{json.dumps(srs, indent=2)}

Approved API Contract:
{json.dumps(api_contract, indent=2)}

Project name:
{project_name}

UI/UX version:
{uiux_version}

User change request:
{change_request or "None"}

Now return ONLY the JSON.
""".strip()


def build_high_fidelity_wireframe_prompt(
    project_name: str,
    screen: UIScreen,
    srs: dict,
    api_contract: dict,
    all_screens: list[dict],
    change_request: str | None = None,
) -> str:
    """
    Builds the LLM prompt for one high-fidelity Tailwind HTML wireframe.

    No fallback/template UI is used.
    The LLM must generate the full screen.
    """

    related_frs = [
        fr for fr in srs.get("functional_requirements", [])
        if fr.get("id") in screen.related_requirements
    ]

    api_paths = list(api_contract.get("paths", {}).keys())

    return f"""
You are a senior UI/UX designer and frontend engineer inside AutoForge.

Generate ONE HIGH-FIDELITY HTML wireframe/prototype screen.

CRITICAL OUTPUT FORMAT:
- Return ONLY a complete HTML document.
- Your response must start with <!DOCTYPE html>
- Your response must end with </html>
- Do NOT include markdown fences.
- Do NOT include explanations.
- Do NOT include text before or after HTML.
- Do NOT use React.
- Do NOT use JavaScript.
- Use Tailwind CSS CDN only.
- Do NOT use external image URLs.
- Use high-fidelity layout: navigation, cards, forms, tables, labels, realistic sections, states, and action buttons.
- The screen must look visually rich and understandable.
- The design must fit a 1366x768 screenshot.
- Do NOT include component list diagrams.
- Do NOT output Mermaid.
- Do NOT output JSON.

Required HTML skeleton:
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>{screen.id} - {screen.name}</title>
    <script src="https://cdn.tailwindcss.com"></script>
</head>
<body>
    <!-- high fidelity UI here -->
</body>
</html>

Project:
{project_name}

Current screen:
{json.dumps(screen.model_dump(), indent=2)}

All generated screens:
{json.dumps(all_screens, indent=2)}

Related functional requirements:
{json.dumps(related_frs, indent=2)}

Approved API paths:
{json.dumps(api_paths, indent=2)}

Business rules:
{json.dumps(srs.get("business_rules", []), indent=2)}

Constraints:
{json.dumps(srs.get("constraints", []), indent=2)}

User change request:
{change_request or "None"}

Design instructions:
- Use a modern e-commerce SaaS/web-app style.
- Use realistic text labels.
- Show navigation appropriate to this screen.
- Show key actions clearly.
- Show empty/error/success states if relevant.
- Use spacing, cards, shadows, rounded corners, clear hierarchy.
- Include the screen ID and related FR IDs somewhere small but visible.
- Generate a unique layout suitable for this specific screen.

Now return ONLY the final complete HTML.
""".strip()