import json
from agents.uiux_agent.schemas import UIScreen


def build_wireframe_prompt(
    project_name: str,
    screen: UIScreen,
    srs: dict,
    api_contract: dict,
    change_request: str | None = None,
) -> str:
    """
    Builds a strict LLM prompt for generating one Tailwind HTML wireframe.

    The LLM must return only complete HTML.
    No markdown.
    No explanations.
    """

    api_paths = list(api_contract.get("paths", {}).keys())

    related_frs = [
        fr for fr in srs.get("functional_requirements", [])
        if fr.get("id") in screen.related_requirements
    ]

    roles = srs.get("roles", [])
    constraints = srs.get("constraints", [])
    business_rules = srs.get("business_rules", [])

    return f"""
You are the UI/UX Agent inside AutoForge, an AI-assisted SDLC automation system.

Your task:
Generate ONE low-fidelity but detailed HTML wireframe for the given UI screen.

IMPORTANT OUTPUT RULES:
- Return ONLY complete HTML.
- Do NOT include markdown fences.
- Do NOT include explanations.
- Do NOT include comments before or after the HTML.
- Use Tailwind CSS CDN.
- Do NOT use external images.
- Use placeholder boxes, labels, cards, tables, forms, buttons, and panels.
- No JavaScript.
- Make the design fit a 1366x768 screenshot.
- Use realistic e-commerce UI labels where relevant.
- The screen must be visually understandable by humans.
- Do NOT create component list diagrams.
- Do NOT output Mermaid.
- Do NOT output React.
- Do NOT output JSON.

HTML requirements:
- Must include <!DOCTYPE html>
- Must include <html>, <head>, and <body>
- Must include this Tailwind CDN:
  <script src="https://cdn.tailwindcss.com"></script>
- Must show the screen ID and screen name in the header.
- Must show related FR IDs in a small footer.

Project:
{project_name}

Screen metadata:
{json.dumps(screen.model_dump(), indent=2)}

Related functional requirements:
{json.dumps(related_frs, indent=2)}

Available user roles:
{json.dumps(roles, indent=2)}

Relevant constraints:
{json.dumps(constraints, indent=2)}

Relevant business rules:
{json.dumps(business_rules, indent=2)}

Approved API paths:
{json.dumps(api_paths, indent=2)}

User refinement/change request:
{change_request or "None"}

Design quality expectations:
- Login/account screens should contain labeled form fields and primary actions.
- Catalog/list screens should contain search, filters, cards, and navigation actions.
- Detail screens should contain preview area, metadata, primary and secondary actions.
- Cart/order screens should contain rows, quantities, totals, and action buttons.
- Checkout screens should contain shipping, payment, validation, and summary sections.
- Admin screens should contain table/list management layouts.
- Error screens should contain visible error details and recovery actions.

Return the final HTML now.
""".strip()