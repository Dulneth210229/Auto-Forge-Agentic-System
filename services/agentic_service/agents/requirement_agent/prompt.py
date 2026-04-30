import json
from agents.requirement_agent.schemas import IntakeInput
from agents.requirement_agent.schemas import SRS


def build_srs_prompt(intake: IntakeInput) -> str:
    intake_json = json.dumps(intake.model_dump(), indent=2)

    return f"""
You are the Requirement Agent for AutoForge.

Generate a Software Requirements Specification for an E-commerce platform.

Return ONLY valid JSON.
Do not include markdown.
Do not include explanations outside JSON.

Rules:
- Domain must be "E-commerce".
- Version must be "v1".
- Functional requirement IDs must be FR-001, FR-002, etc.
- Non-functional requirement IDs must be NFR-001, NFR-002, etc.
- Acceptance criteria IDs must be AC-001, AC-002, etc.
- Use case IDs must be UC-001, UC-002, etc.
- Include catalog, product details, cart, checkout, order placement, and order history.
- Include roles, workflows, business rules, constraints, assumptions.
- Do NOT include component list diagrams.

Input:
{intake_json}

Required JSON structure:
{{
  "project_name": "...",
  "version": "v1",
  "domain": "E-commerce",
  "purpose": "...",
  "scope_in": [],
  "scope_out": [],
  "roles": [],
  "stakeholders": [],
  "workflows": [],
  "business_rules": [],
  "constraints": [],
  "assumptions": [],
  "functional_requirements": [
    {{
      "id": "FR-001",
      "title": "...",
      "description": "...",
      "priority": "Must",
      "acceptance_criteria": [
        {{
          "id": "AC-001",
          "description": "..."
        }}
      ]
    }}
  ],
  "non_functional_requirements": [
    {{
      "id": "NFR-001",
      "category": "Performance",
      "description": "...",
      "acceptance_criteria": [
        {{
          "id": "AC-010",
          "description": "..."
        }}
      ]
    }}
  ],
  "use_cases": [
    {{
      "id": "UC-001",
      "title": "...",
      "actor": "...",
      "preconditions": [],
      "main_flow": [],
      "alternative_flows": [],
      "related_requirements": ["FR-001"]
    }}
  ]
}}
"""

def build_srs_revision_prompt(existing_srs: SRS, change_request: str, new_version: str) -> str:
    existing_json = json.dumps(existing_srs.model_dump(), indent=2)

    return f"""
You are the Requirement Agent for AutoForge.

The user wants to revise an existing SRS.

Return ONLY valid JSON.
Do not include markdown.
Do not include explanation outside JSON.

Rules:
- Keep the same SRS structure.
- Update the version to "{new_version}".
- Preserve all existing valid requirements unless the user asks to remove/change them.
- Add new requirements with the next available IDs.
- Functional requirement IDs must follow FR-001, FR-002, etc.
- Non-functional requirement IDs must follow NFR-001, NFR-002, etc.
- Acceptance criteria IDs must follow AC-001, AC-002, etc.
- Use case IDs must follow UC-001, UC-002, etc.
- Keep E-commerce domain only.
- Do NOT include component list diagrams.

Existing SRS:
{existing_json}

User change request:
{change_request}

Now return the revised complete SRS JSON.
"""