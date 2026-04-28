import json
from agents.requirement_agent.schemas import IntakeInput


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