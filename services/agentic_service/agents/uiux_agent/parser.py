import json
import re
from typing import Any

from agents.uiux_agent.schemas import UIScreen, UserFlow, UITraceLink


class UIUXParseError(Exception):
    pass


class WireframeParseError(Exception):
    pass


# ---------------------------------------------------------------------
# JSON extraction / repair
# ---------------------------------------------------------------------

def extract_json_object(raw_output: str) -> dict:
    """
    Extracts one JSON object from LLM output.

    Local Ollama models sometimes return:
    - markdown fences
    - extra explanation text
    - JSON-like output with minor formatting mistakes

    This function first tries strict JSON parsing.
    If json-repair is installed, it also tries repairing broken JSON.
    """

    if not raw_output:
        raise UIUXParseError("LLM output is empty.")

    text = raw_output.strip()

    text = re.sub(r"```json", "", text, flags=re.IGNORECASE).strip()
    text = re.sub(r"```", "", text).strip()

    start = text.find("{")
    end = text.rfind("}")

    if start == -1 or end == -1 or end <= start:
        raise UIUXParseError("No JSON object found in LLM output.")

    json_text = text[start:end + 1]

    try:
        return json.loads(json_text)
    except json.JSONDecodeError as strict_error:
        try:
            from json_repair import repair_json

            repaired = repair_json(json_text)
            return json.loads(repaired)
        except Exception as repair_error:
            raise UIUXParseError(
                "Invalid JSON from LLM. "
                f"Strict error: {strict_error}. "
                f"Repair error: {repair_error}. "
                f"First 800 chars: {json_text[:800]}"
            ) from repair_error


# ---------------------------------------------------------------------
# Key normalization
# ---------------------------------------------------------------------

def normalize_plan_keys(data: dict) -> dict:
    """
    Repairs common top-level key names returned by local LLMs.
    """

    normalized = dict(data)

    aliases = {
        "ui_screens": "screens",
        "uiScreens": "screens",
        "screen_inventory": "screens",
        "screenInventory": "screens",
        "pages": "screens",
        "wireframes": "screens",

        "flows": "user_flows",
        "flow": "user_flows",
        "user_flow": "user_flows",
        "userFlows": "user_flows",
        "userFlow": "user_flows",
        "journeys": "user_flows",
        "journey": "user_flows",

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


# ---------------------------------------------------------------------
# General helpers
# ---------------------------------------------------------------------

def _slugify(value: str) -> str:
    return (
        str(value)
        .lower()
        .replace("/", " ")
        .replace("&", "and")
        .replace("-", " ")
        .replace("{", "")
        .replace("}", "")
        .replace(":", "")
        .replace(";", "")
        .strip()
        .replace("  ", " ")
        .replace(" ", "_")
    )


def _safe_list(value: Any) -> list:
    if value is None:
        return []

    if isinstance(value, list):
        return value

    if isinstance(value, str):
        return [value]

    return []


def _clean_fr_ids(value: Any) -> list[str]:
    """
    Normalizes related requirement IDs.
    """

    items = _safe_list(value)
    cleaned = []

    for item in items:
        if not item:
            continue

        text = str(item).strip()

        # Extract FR IDs if the model returns long text.
        matches = re.findall(r"FR-\d{3}", text, flags=re.IGNORECASE)

        if matches:
            cleaned.extend([match.upper() for match in matches])
        else:
            cleaned.append(text)

    # remove duplicates while preserving order
    unique = []
    for item in cleaned:
        if item not in unique:
            unique.append(item)

    return unique


def _is_weak_label(label: str | None) -> bool:
    if not label:
        return True

    text = str(label).strip().lower()

    if not text:
        return True

    weak_exact = {
        "step",
        "screen",
        "page",
        "next",
        "action",
        "flow",
        "node",
        "user action",
        "process",
        "continue",
    }

    if text in weak_exact:
        return True

    if re.fullmatch(r"step\s*\d+", text):
        return True

    if re.fullmatch(r"screen\s*\d+", text):
        return True

    if re.fullmatch(r"page\s*\d+", text):
        return True

    return False


def _action_label_from_screen_name(screen_name: str) -> str:
    """
    Converts a screen name into a meaningful user-flow action label.
    """

    name = str(screen_name).strip()
    lower = name.lower()

    if "home" in lower:
        return "Open Storefront Home"
    if "catalog" in lower or "product list" in lower or "products" == lower:
        return "Browse Product Catalog"
    if "detail" in lower:
        return "View Product Details"
    if "wishlist" in lower:
        return "Review Saved Wishlist Items"
    if "cart" in lower:
        return "Review Shopping Cart"
    if "checkout" in lower:
        return "Complete Checkout Details"
    if "payment" in lower:
        return "Submit Payment Information"
    if "order placement" in lower or "confirmation" in lower or "success" in lower:
        return "View Order Confirmation"
    if "order history" in lower or "orders" in lower:
        return "View Order History"
    if "return" in lower or "refund" in lower:
        return "Request Return or Refund"
    if "login" in lower or "sign in" in lower:
        return "Sign In to Account"
    if "register" in lower or "sign up" in lower or "account access" in lower:
        return "Create or Access Account"
    if "admin" in lower and "product" in lower:
        return "Manage Product Inventory"
    if "admin" in lower:
        return "Open Admin Dashboard"

    return name


def _edge_condition_from_labels(from_label: str, to_label: str, index: int) -> str:
    """
    Generates useful transition labels for user-flow edges.
    """

    to_lower = to_label.lower()

    if index == 1:
        return "Customer starts journey"
    if "catalog" in to_lower or "browse" in to_lower:
        return "Open product browsing"
    if "detail" in to_lower:
        return "Select product"
    if "cart" in to_lower:
        return "Add item to cart"
    if "checkout" in to_lower:
        return "Proceed to checkout"
    if "payment" in to_lower:
        return "Continue to payment"
    if "confirmation" in to_lower or "order" in to_lower and "history" not in to_lower:
        return "Place order"
    if "history" in to_lower:
        return "View previous orders"
    if "return" in to_lower or "refund" in to_lower:
        return "Request support action"
    if "admin" in to_lower or "manage" in to_lower:
        return "Open management area"

    return "Continue"


# ---------------------------------------------------------------------
# Screen normalization
# ---------------------------------------------------------------------

def _normalize_screen(item: dict, index: int) -> dict:
    """
    Normalizes one LLM-generated screen.

    This does not hardcode screens.
    It only repairs missing/variant fields returned by the LLM.
    """

    screen = dict(item)

    if not screen.get("id"):
        screen["id"] = screen.get("screen_id") or screen.get("screenId") or f"UI-SCR-{index:02d}"

    if "title" in screen and "name" not in screen:
        screen["name"] = screen["title"]

    if "screen_name" in screen and "name" not in screen:
        screen["name"] = screen["screen_name"]

    if "screenName" in screen and "name" not in screen:
        screen["name"] = screen["screenName"]

    screen.setdefault("name", f"Generated Screen {index}")

    safe_name = _slugify(screen["name"])

    if "filename" in screen and "file_name" not in screen:
        screen["file_name"] = screen["filename"]

    if "file" in screen and "file_name" not in screen:
        screen["file_name"] = screen["file"]

    if "html_file" in screen and "file_name" not in screen:
        screen["file_name"] = screen["html_file"]

    screen.setdefault("file_name", f"{screen['id']}_{safe_name}.html")
    screen.setdefault("description", f"Generated UI screen for {screen['name']}.")
    screen.setdefault("route", "/" + safe_name.replace("_", "-"))

    related = (
        screen.get("related_requirements")
        or screen.get("requirements")
        or screen.get("requirement_ids")
        or screen.get("fr_ids")
        or []
    )

    screen["related_requirements"] = _clean_fr_ids(related)

    return screen


# ---------------------------------------------------------------------
# Flow normalization
# ---------------------------------------------------------------------

def _normalize_node(item: dict, index: int, screen_lookup: dict[str, dict]) -> dict:
    """
    Normalizes one LLM-generated flow node.
    Repairs weak labels like 'Step 3' using linked screen names.
    """

    node = dict(item)

    if not node.get("id"):
        node["id"] = node.get("node_id") or node.get("nodeId") or f"FLOW-N{index:02d}"

    if "name" in node and "label" not in node:
        node["label"] = node["name"]

    if "title" in node and "label" not in node:
        node["label"] = node["title"]

    node.setdefault("label", f"Step {index}")

    screen_id = node.get("screen_id") or node.get("screenId")
    node["screen_id"] = screen_id

    related = (
        node.get("related_requirements")
        or node.get("requirements")
        or node.get("requirement_ids")
        or []
    )
    node["related_requirements"] = _clean_fr_ids(related)

    if _is_weak_label(node.get("label")):
        if screen_id and screen_id in screen_lookup:
            node["label"] = _action_label_from_screen_name(screen_lookup[screen_id]["name"])
            if not node["related_requirements"]:
                node["related_requirements"] = screen_lookup[screen_id].get("related_requirements", [])
        elif index == 1:
            node["label"] = "Start Journey"
        else:
            node["label"] = f"Continue Journey Step {index}"

    return node


def _normalize_edge(item: dict) -> dict:
    edge = dict(item)

    if "from" in edge and "from_node" not in edge:
        edge["from_node"] = edge["from"]

    if "source" in edge and "from_node" not in edge:
        edge["from_node"] = edge["source"]

    if "fromNode" in edge and "from_node" not in edge:
        edge["from_node"] = edge["fromNode"]

    if "to" in edge and "to_node" not in edge:
        edge["to_node"] = edge["to"]

    if "target" in edge and "to_node" not in edge:
        edge["to_node"] = edge["target"]

    if "toNode" in edge and "to_node" not in edge:
        edge["to_node"] = edge["toNode"]

    if "label" in edge and "condition" not in edge:
        edge["condition"] = edge["label"]

    edge.setdefault("condition", None)

    return edge


def _build_flow_from_screens(screens: list[dict]) -> dict:
    """
    Builds a valid user flow from LLM-generated screens.

    This is not a static screen template.
    It only connects screens that the LLM already generated.
    """

    nodes = [
        {
            "id": "FLOW-N01",
            "label": "Start Journey",
            "screen_id": None,
            "related_requirements": [],
        }
    ]

    for index, screen in enumerate(screens, start=2):
        nodes.append(
            {
                "id": f"FLOW-N{index:02d}",
                "label": _action_label_from_screen_name(screen["name"]),
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
                "condition": _edge_condition_from_labels(
                    nodes[index - 1]["label"],
                    nodes[index]["label"],
                    index,
                ),
            }
        )

    return {
        "id": "UF-001",
        "name": "Main Customer Journey",
        "actor": "Customer",
        "nodes": nodes,
        "edges": edges,
    }


def _normalize_flow(item: dict, index: int, screens: list[dict]) -> dict:
    """
    Normalizes one LLM-generated flow.

    If the LLM gives empty nodes or generic node labels, this repairs the flow
    using LLM-generated screen names.
    """

    screen_lookup = {screen["id"]: screen for screen in screens}

    flow = dict(item)

    flow.setdefault("id", f"UF-{index:03d}")
    flow.setdefault("name", "Main Customer Journey")
    flow.setdefault("actor", "Customer")

    if not flow.get("nodes") and "steps" in flow:
        flow["nodes"] = flow["steps"]

    flow.setdefault("nodes", [])
    flow.setdefault("edges", [])

    if not flow["nodes"]:
        return _build_flow_from_screens(screens)

    normalized_nodes = [
        _normalize_node(node, node_index, screen_lookup)
        for node_index, node in enumerate(flow["nodes"], start=1)
        if isinstance(node, dict)
    ]

    if not normalized_nodes:
        return _build_flow_from_screens(screens)

    # If every useful node is weak or disconnected from screens, rebuild from screens.
    linked_screen_count = sum(1 for node in normalized_nodes if node.get("screen_id"))
    if linked_screen_count == 0 and screens:
        return _build_flow_from_screens(screens)

    normalized_edges = [
        _normalize_edge(edge)
        for edge in flow["edges"]
        if isinstance(edge, dict)
    ]

    # Keep only edges that reference existing nodes.
    node_ids = {node["id"] for node in normalized_nodes}
    normalized_edges = [
        edge for edge in normalized_edges
        if edge.get("from_node") in node_ids and edge.get("to_node") in node_ids
    ]

    if not normalized_edges and len(normalized_nodes) > 1:
        for edge_index in range(1, len(normalized_nodes)):
            from_label = normalized_nodes[edge_index - 1]["label"]
            to_label = normalized_nodes[edge_index]["label"]

            normalized_edges.append(
                {
                    "from_node": normalized_nodes[edge_index - 1]["id"],
                    "to_node": normalized_nodes[edge_index]["id"],
                    "condition": _edge_condition_from_labels(from_label, to_label, edge_index),
                }
            )

    # Improve weak edge labels.
    for edge_index, edge in enumerate(normalized_edges, start=1):
        if not edge.get("condition") or _is_weak_label(edge.get("condition")):
            from_node = next((node for node in normalized_nodes if node["id"] == edge["from_node"]), None)
            to_node = next((node for node in normalized_nodes if node["id"] == edge["to_node"]), None)

            if from_node and to_node:
                edge["condition"] = _edge_condition_from_labels(
                    from_node["label"],
                    to_node["label"],
                    edge_index,
                )
            else:
                edge["condition"] = "Continue"

    flow["nodes"] = normalized_nodes
    flow["edges"] = normalized_edges

    return flow


# ---------------------------------------------------------------------
# Traceability
# ---------------------------------------------------------------------

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


def _normalize_trace_link(item: dict) -> dict:
    link = dict(item)

    if "requirement" in link and "requirement_id" not in link:
        link["requirement_id"] = link["requirement"]

    if "fr_id" in link and "requirement_id" not in link:
        link["requirement_id"] = link["fr_id"]

    if "screen" in link and "screen_id" not in link:
        link["screen_id"] = link["screen"]

    if "screenName" in link and "screen_name" not in link:
        link["screen_name"] = link["screenName"]

    link.setdefault("reason", "Generated traceability link from requirement to UI screen.")

    return link


# ---------------------------------------------------------------------
# Public plan parser
# ---------------------------------------------------------------------

def parse_uiux_plan(raw_output: str) -> tuple[list[UIScreen], list[UserFlow], list[UITraceLink]]:
    """
    Parses and normalizes LLM-generated UI/UX plan.

    Important:
    - Screens still come from LLM output.
    - Flow repairs only use LLM-generated screens.
    - No predefined UI screens are created here.
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

    if not isinstance(raw_flows, list):
        raw_flows = [raw_flows]

    flows_dicts = [
        _normalize_flow(item, index, screens_dicts)
        for index, item in enumerate(raw_flows, start=1)
        if isinstance(item, dict)
    ]

    if not flows_dicts:
        flows_dicts = [_build_flow_from_screens(screens_dicts)]

    if not raw_trace:
        raw_trace = _build_missing_traceability(screens_dicts)

    if not isinstance(raw_trace, list):
        raw_trace = [raw_trace]

    trace_dicts = [
        _normalize_trace_link(item)
        for item in raw_trace
        if isinstance(item, dict)
    ]

    screens = [UIScreen.model_validate(item) for item in screens_dicts]
    user_flows = [UserFlow.model_validate(item) for item in flows_dicts]
    traceability = [UITraceLink.model_validate(item) for item in trace_dicts]

    if not user_flows:
        raise UIUXParseError("LLM returned zero valid user flows.")

    return screens, user_flows, traceability


# ---------------------------------------------------------------------
# HTML cleaning / quality validation
# ---------------------------------------------------------------------

def _extract_html_fragment(text: str) -> str | None:
    lower_text = text.lower()

    candidates = ["<main", "<section", "<div", "<body"]

    starts = [
        lower_text.find(candidate)
        for candidate in candidates
        if lower_text.find(candidate) != -1
    ]

    if not starts:
        return None

    return text[min(starts):].strip()


def _wrap_fragment_as_html(fragment: str) -> str:
    """
    Wraps LLM-generated UI content inside a valid HTML shell.

    This is not a UI template.
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


def _html_quality_score(html: str) -> int:
    """
    Checks whether the LLM-generated wireframe is detailed enough.

    This does not create UI content.
    It only rejects weak outputs so the repair prompt can regenerate them.
    """

    score = 0
    lower = html.lower()

    if len(html) > 2500:
        score += 1

    if len(html) > 3500:
        score += 1

    if "tailwindcss" in lower:
        score += 1

    if "<nav" in lower or "navigation" in lower or "header" in lower:
        score += 1

    if "<form" in lower or "<input" in lower or "<button" in lower:
        score += 1

    if "grid" in lower or "flex" in lower:
        score += 1

    if "shadow" in lower or "rounded" in lower or "border" in lower:
        score += 1

    if "card" in lower or "summary" in lower or "table" in lower or "filter" in lower:
        score += 1

    if "price" in lower or "order" in lower or "cart" in lower or "product" in lower:
        score += 1

    return score


def clean_html_output(raw_output: str) -> str:
    """
    Cleans and validates LLM-generated HTML.

    Accepts:
    - complete HTML documents
    - body-only HTML
    - main/section/div fragments

    It does not use predefined wireframe templates.
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

    if _html_quality_score(html) < 5:
        raise WireframeParseError("LLM HTML is too weak for high-fidelity wireframe.")

    return html