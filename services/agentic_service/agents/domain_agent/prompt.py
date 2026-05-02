import json


def build_domain_pack_prompt(srs: dict, retrieved_chunks: list[dict], version: str) -> str:
    """
    Builds the LLM prompt for DomainPack generation.

    Important:
    - The LLM must use SRS + retrieved domain knowledge.
    - The output must be valid JSON.
    - The output will be validated by Pydantic.
    """

    srs_json = json.dumps(srs, indent=2)
    knowledge_json = json.dumps(retrieved_chunks, indent=2)

    return f"""
You are the Domain Agent for AutoForge.

Your job is to generate an E-commerce Domain Workflow and Rules Pack.

Use:
1. The approved SRS
2. The retrieved E-commerce domain knowledge chunks

Return ONLY valid JSON.
Do not include markdown.
Do not include explanations outside the JSON.

Rules:
- Domain must be "E-commerce".
- Version must be "{version}".
- Workflow IDs must be WF-001, WF-002, etc.
- Business rule IDs must be BR-001, BR-002, etc.
- Domain entity IDs must be DE-001, DE-002, etc.
- Exception IDs must be EX-001, EX-002, etc.
- Include at minimum:
  - Product browsing workflow
  - Product detail workflow
  - Cart workflow
  - Checkout workflow
  - Order placement workflow
  - Order history workflow
- Include E-commerce rules about stock, pricing, discounts, checkout, order creation, cancellation, and payment failure if relevant.
- Preserve traceability by linking workflows and rules to FR IDs from the SRS.
- Do NOT include component list diagrams.

Approved SRS:
{srs_json}

Retrieved domain knowledge:
{knowledge_json}

Required JSON structure:
{{
  "project_name": "...",
  "version": "{version}",
  "domain": "E-commerce",
  "overview": "...",
  "workflows": [
    {{
      "id": "WF-001",
      "name": "Product Browsing",
      "description": "...",
      "actors": ["Customer"],
      "steps": ["..."],
      "exceptions": ["..."],
      "related_requirements": ["FR-001"]
    }}
  ],
  "business_rules": [
    {{
      "id": "BR-001",
      "title": "...",
      "description": "...",
      "related_requirements": ["FR-001"]
    }}
  ],
  "domain_entities": [
    {{
      "id": "DE-001",
      "name": "Product",
      "description": "...",
      "key_attributes": ["product_id", "name", "price", "stock_quantity"]
    }}
  ],
  "exceptions": [
    {{
      "id": "EX-001",
      "name": "Out of Stock",
      "description": "...",
      "handling_rule": "..."
    }}
  ],
  "assumptions": ["..."],
  "constraints": ["..."],
  "retrieved_knowledge": []
}}
"""