import json
import re

from agents.uiux_agent.schemas import UIScreen, UserFlow, UITraceLink


class UIUXParseError(Exception):
    pass


class WireframeParseError(Exception):
    pass


def extract_json_object(raw_output: str) -> dict:
    """
    Extract one JSON object from LLM output.
    """

    if not raw_output:
        raise UIUXParseError("LLM output is empty.")

    text = raw_output.strip()
    text = re.sub(r"```json", "", text, flags=re.IGNORECASE).strip()
    text = re.sub(r"```", "", text).strip()

    start = text.find("{")
    end = text.rfind("}")

    if start == -1 or end == -1:
        raise UIUXParseError("No JSON object found in LLM output.")

    try:
        return json.loads(text[start:end + 1])
    except json.JSONDecodeError as error:
        raise UIUXParseError(f"Invalid JSON from LLM: {error}") from error


def normalize_plan_keys(data: dict) -> dict:
    """
    Repairs common key names returned by local LLMs.
    """

    normalized = dict(data)

    aliases = {
        "ui_screens": "screens",
        "uiScreens": "screens",
        "screen_inventory": "screens",
        "screenInventory": "screens",
        "pages": "screens",
        "flows": "user_flows",
        "flow": "user_flows",
        "user_flow": "user_flows",
        "userFlows": "user_flows",
        "trace_links": "traceability",
        "traceability_links": "traceability",
        "traceabilityLinks": "traceability",
        "requirement_mapping": "traceability",
        "requirements_mapping": "traceability",
    }

    for wrong_key, correct_key in aliases.items():
        if correct_key not in normalized and wrong_key in normalized:
            normalized[correct_key] = normalized[wrong_key]

    return normalized


def _slugify(value: str) -> str:
    return (
        value.lower()
        .replace("/", " ")
        .replace("&", "and")
        .replace("-", " ")
        .replace("{", "")
        .replace("}", "")
        .strip()
        .replace("  ", " ")
        .replace(" ", "_")
    )


def _normalize_screen(item: dict, index: int) -> dict:
    """
    Normalizes one LLM-generated screen.
    """

    screen = dict(item)

    if not screen.get("id"):
        screen["id"] = screen.get("screen_id") or f"UI-SCR-{index:02d}"

    if "title" in screen and "name" not in screen:
        screen["name"] = screen["title"]

    screen.setdefault("name", f"Generated Screen {index}")

    safe_name = _slugify(screen["name"])

    if "filename" in screen and "file_name" not in screen:
        screen["file_name"] = screen["filename"]

    if "file" in screen and "file_name" not in screen:
        screen["file_name"] = screen["file"]

    screen.setdefault("file_name", f"{screen['id']}_{safe_name}.html")
    screen.setdefault("description", f"Generated UI screen for {screen['name']}.")
    screen.setdefault("route", "/" + safe_name.replace("_", "-"))
    screen.setdefault("related_requirements", [])

    if screen["related_requirements"] is None:
        screen["related_requirements"] = []

    return screen


def _normalize_edge(item: dict) -> dict:
    edge = dict(item)

    if "from" in edge and "from_node" not in edge:
        edge["from_node"] = edge["from"]

    if "source" in edge and "from_node" not in edge:
        edge["from_node"] = edge["source"]

    if "to" in edge and "to_node" not in edge:
        edge["to_node"] = edge["to"]

    if "target" in edge and "to_node" not in edge:
        edge["to_node"] = edge["target"]

    edge.setdefault("condition", None)

    return edge


def _build_flow_from_screens(screens: list[dict]) -> dict:
    """
    Builds a valid user flow from LLM-generated screens.

    This is not a hardcoded screen template.
    It only connects the screens that the LLM already generated.
    """

    nodes = [
        {
            "id": "FLOW-N01",
            "label": "Start",
            "screen_id": None,
            "related_requirements": [],
        }
    ]

    for index, screen in enumerate(screens, start=2):
        nodes.append(
            {
                "id": f"FLOW-N{index:02d}",
                "label": screen["name"],
                "screen_id": screen["id"],
                "related_requirements": screen.get("related_requirements", []),
            }
        )

    edges = []

    for index in range(1, len(nodes)):
        edges.append(
            {
                "from_node": nodes[index - 1]["id"],
                "to_node": nodes[index]["id"],
                "condition": "Next step" if index > 1 else "Start journey",
            }
        )

    return {
        "id": "UF-001",
        "name": "Auto-generated UI Flow",
        "actor": "Customer",
        "nodes": nodes,
        "edges": edges,
    }


def _normalize_flow(item: dict, index: int, screens: list[dict]) -> dict:
    """
    Normalizes one LLM-generated flow.

    If the LLM returns empty nodes/edges, this repairs the flow using
    the LLM-generated screens.
    """

    flow = dict(item)

    flow.setdefault("id", f"UF-{index:03d}")
    flow.setdefault("name", "Main User Flow")
    flow.setdefault("actor", "Customer")

    if not flow.get("nodes") and "steps" in flow:
        flow["nodes"] = flow["steps"]

    flow.setdefault("nodes", [])
    flow.setdefault("edges", [])

    if not flow["nodes"]:
        return _build_flow_from_screens(screens)

    normalized_nodes = []

    for node_index, node in enumerate(flow["nodes"], start=1):
        if not isinstance(node, dict):
            continue

        item_node = dict(node)

        if not item_node.get("id"):
            item_node["id"] = f"FLOW-N{node_index:02d}"

        if "name" in item_node and "label" not in item_node:
            item_node["label"] = item_node["name"]

        item_node.setdefault("label", f"Step {node_index}")
        item_node.setdefault("screen_id", None)
        item_node.setdefault("related_requirements", [])

        if item_node["related_requirements"] is None:
            item_node["related_requirements"] = []

        normalized_nodes.append(item_node)

    normalized_edges = [
        _normalize_edge(edge)
        for edge in flow["edges"]
        if isinstance(edge, dict)
    ]

    if not normalized_edges and len(normalized_nodes) > 1:
        for edge_index in range(1, len(normalized_nodes)):
            normalized_edges.append(
                {
                    "from_node": normalized_nodes[edge_index - 1]["id"],
                    "to_node": normalized_nodes[edge_index]["id"],
                    "condition": "Next step",
                }
            )

    flow["nodes"] = normalized_nodes
    flow["edges"] = normalized_edges

    return flow


def _build_missing_traceability(screens: list[dict]) -> list[dict]:
    links = []

    for screen in screens:
        for fr_id in screen.get("related_requirements", []):
            links.append(
                {
                    "requirement_id": fr_id,
                    "screen_id": screen["id"],
                    "screen_name": screen["name"],
                    "reason": f"{screen['name']} supports {fr_id}.",
                }
            )

    return links


def parse_uiux_plan(raw_output: str) -> tuple[list[UIScreen], list[UserFlow], list[UITraceLink]]:
    """
    Parse and normalize LLM-generated UI/UX plan.
    """

    data = normalize_plan_keys(extract_json_object(raw_output))

    if "screens" not in data:
        raise UIUXParseError(
            f"UI/UX plan missing screens. Returned keys: {list(data.keys())}"
        )

    raw_screens = data.get("screens") or []
    raw_flows = data.get("user_flows") or []
    raw_trace = data.get("traceability") or []

    if not isinstance(raw_screens, list):
        raise UIUXParseError("'screens' must be a list.")

    screens_dicts = [
        _normalize_screen(item, index)
        for index, item in enumerate(raw_screens, start=1)
        if isinstance(item, dict)
    ]

    if not screens_dicts:
        raise UIUXParseError("LLM returned zero valid screens.")

    if not raw_flows:
        raw_flows = [_build_flow_from_screens(screens_dicts)]

    flows_dicts = [
        _normalize_flow(item, index, screens_dicts)
        for index, item in enumerate(raw_flows, start=1)
        if isinstance(item, dict)
    ]

    if not raw_trace:
        raw_trace = _build_missing_traceability(screens_dicts)

    screens = [UIScreen.model_validate(item) for item in screens_dicts]
    user_flows = [UserFlow.model_validate(item) for item in flows_dicts]
    traceability = [
        UITraceLink.model_validate(item)
        for item in raw_trace
        if isinstance(item, dict)
    ]

    if not user_flows:
        raise UIUXParseError("LLM returned zero valid user flows.")

    return screens, user_flows, traceability


def _extract_html_fragment(text: str) -> str | None:
    """
    Extracts a usable HTML fragment if the model did not return complete HTML.
    """

    lower_text = text.lower()

    candidates = ["<main", "<section", "<div", "<body"]

    starts = [
        lower_text.find(candidate)
        for candidate in candidates
        if lower_text.find(candidate) != -1
    ]

    if not starts:
        return None

    start = min(starts)

    return text[start:].strip()


def _wrap_fragment_as_html(fragment: str) -> str:
    """
    Wraps LLM-generated UI content inside a valid HTML shell.

    This is not a UI template. It only provides required HTML boilerplate.
    The actual UI content is still generated by the LLM.
    """

    if "<body" in fragment.lower():
        body = fragment
    else:
        body = f"""
<body class="bg-slate-100 text-slate-900">
{fragment}
</body>
"""

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Generated Wireframe</title>
    <script src="https://cdn.tailwindcss.com"></script>
</head>
{body}
</html>"""


def clean_html_output(raw_output: str) -> str:
    """
    Clean and validate LLM-generated HTML.

    This accepts:
    - complete HTML documents
    - body-only HTML
    - main/section/div fragments

    It does not generate UI content itself.
    """

    if not raw_output:
        raise WireframeParseError("LLM output is empty.")

    text = raw_output.strip()
    text = re.sub(r"```html", "", text, flags=re.IGNORECASE).strip()
    text = re.sub(r"```", "", text).strip()

    lower_text = text.lower()

    html_start = lower_text.find("<!doctype html")
    if html_start == -1:
        html_start = lower_text.find("<html")

    html_end = lower_text.rfind("</html>")

    if html_start != -1 and html_end != -1:
        html = text[html_start:html_end + len("</html>")]
    else:
        fragment = _extract_html_fragment(text)

        if not fragment:
            raise WireframeParseError("LLM output does not contain usable HTML.")

        html = _wrap_fragment_as_html(fragment)

    if "tailwindcss" not in html.lower():
        html = html.replace(
            "</head>",
            '    <script src="https://cdn.tailwindcss.com"></script>\n</head>',
        )

    if "<html" not in html.lower():
        raise WireframeParseError("HTML tag missing.")

    if "<head" not in html.lower():
        raise WireframeParseError("Head tag missing.")

    if "<body" not in html.lower():
        raise WireframeParseError("Body tag missing.")

    if "</html>" not in html.lower():
        raise WireframeParseError("Closing HTML tag missing.")

    return html