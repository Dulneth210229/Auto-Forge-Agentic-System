import json
import re
from agents.requirement_agent.schemas import SRS


class SRSParseError(Exception):
    pass


def extract_json(text: str) -> dict:
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    match = re.search(r"\{.*\}", text, re.DOTALL)

    if not match:
        raise SRSParseError("No JSON object found in LLM output.")

    try:
        return json.loads(match.group(0))
    except json.JSONDecodeError as error:
        raise SRSParseError(f"Invalid JSON extracted: {error}")


def stringify_list_items(items):
    """
    Converts LLM-generated object lists into simple string lists.
    Example:
    [{"id": "BR-001", "title": "Stock rule", "description": "Only in-stock products can be ordered"}]
    becomes:
    ["Stock rule - Only in-stock products can be ordered"]
    """
    if not isinstance(items, list):
        return []

    normalized = []

    for item in items:
        if isinstance(item, str):
            normalized.append(item)

        elif isinstance(item, dict):
            title = item.get("title", "")
            description = item.get("description", "")
            name = item.get("name", "")
            step = item.get("step", "")

            text_parts = [part for part in [title, description, name, step] if part]

            if text_parts:
                normalized.append(" - ".join(text_parts))
            else:
                normalized.append(json.dumps(item))

        else:
            normalized.append(str(item))

    return normalized


def normalize_srs_data(data: dict) -> dict:
    simple_string_lists = [
        "scope_in",
        "scope_out",
        "roles",
        "workflows",
        "business_rules",
        "constraints",
        "assumptions",
    ]

    for field in simple_string_lists:
        data[field] = stringify_list_items(data.get(field, []))

    for use_case in data.get("use_cases", []):
        use_case["preconditions"] = stringify_list_items(use_case.get("preconditions", []))
        use_case["main_flow"] = stringify_list_items(use_case.get("main_flow", []))
        use_case["alternative_flows"] = stringify_list_items(use_case.get("alternative_flows", []))

    return data


def parse_srs(text: str) -> SRS:
    data = extract_json(text)
    data = normalize_srs_data(data)
    return SRS.model_validate(data)