from agents.uiux_agent.schemas import UserFlow


def _safe_mermaid_id(value: str, index: int) -> str:
    """
    Mermaid node IDs should be simple and safe.
    LLM may return IDs like FLOW-N01, which can cause Mermaid syntax issues.
    We map them to safe IDs like N01, N02, etc.
    """
    return f"N{index:02d}"


def build_mermaid_from_flow(flow: UserFlow) -> str:
    """
    Converts an LLM-generated UserFlow object into Mermaid syntax.

    This file does not decide screens.
    It only renders the LLM-generated flow.
    """

    lines = ["flowchart TD"]
    id_map = {}

    for index, node in enumerate(flow.nodes, start=1):
        safe_id = _safe_mermaid_id(node.id, index)
        id_map[node.id] = safe_id

        label = node.label

        if node.screen_id:
            label = f"{node.screen_id} {node.label}"

        label = label.replace('"', "'")

        if node.label.lower().strip() == "start":
            lines.append(f'    {safe_id}(["{label}"])')
        else:
            lines.append(f'    {safe_id}["{label}"]')

    lines.append("")

    for edge in flow.edges:
        from_id = id_map.get(edge.from_node)
        to_id = id_map.get(edge.to_node)

        if not from_id or not to_id:
            continue

        if edge.condition:
            condition = edge.condition.replace('"', "'")
            lines.append(f'    {from_id} -->|"{condition}"| {to_id}')
        else:
            lines.append(f"    {from_id} --> {to_id}")

    return "\n".join(lines)