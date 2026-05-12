from agents.uiux_agent.schemas import UserFlow


def build_mermaid_from_flow(flow: UserFlow) -> str:
    """
    Converts a UserFlow into a readable Mermaid flowchart.

    The LLM generates the actual flow.
    This function only improves Mermaid visibility and layout.
    """

    if not flow.nodes:
        return "\n".join([
            "flowchart TD",
            '    N01(["Start Journey"])',
            '    N02["No user flow data generated"]',
            "    N01 --> N02",
        ])

    lines = [
        "flowchart TD",
        "",
        "    classDef start fill:#dbeafe,stroke:#2563eb,stroke-width:2px,color:#111827;",
        "    classDef screen fill:#ecfccb,stroke:#65a30d,stroke-width:1.5px,color:#111827;",
        "    classDef decision fill:#fef3c7,stroke:#d97706,stroke-width:1.5px,color:#111827;",
        "    classDef endNode fill:#fee2e2,stroke:#dc2626,stroke-width:2px,color:#111827;",
        ""
    ]

    id_map = {}

    for index, node in enumerate(flow.nodes, start=1):
        safe_id = f"N{index:02d}"
        id_map[node.id] = safe_id

        label = node.label or f"Flow Step {index}"

        # Make label readable in diagram.
        if node.screen_id:
            label = f"{label}\\n({node.screen_id})"

        label = label.replace('"', "'")

        lower_label = label.lower()

        if index == 1 or "start" in lower_label:
            lines.append(f'    {safe_id}(["{label}"]):::start')
        elif "confirm" in lower_label or "success" in lower_label or "order placed" in lower_label:
            lines.append(f'    {safe_id}(["{label}"]):::endNode')
        elif "decision" in lower_label or "valid" in lower_label or "available" in lower_label:
            lines.append(f'    {safe_id}{{"{label}"}}:::decision')
        else:
            lines.append(f'    {safe_id}["{label}"]:::screen')

    lines.append("")

    edge_count = 0

    for edge in flow.edges:
        from_id = id_map.get(edge.from_node)
        to_id = id_map.get(edge.to_node)

        if not from_id or not to_id:
            continue

        edge_count += 1

        if edge.condition:
            condition = edge.condition.replace('"', "'")
            lines.append(f'    {from_id} -->|"{condition}"| {to_id}')
        else:
            lines.append(f"    {from_id} --> {to_id}")

    # If LLM gave nodes but bad/missing edges, connect sequentially.
    if edge_count == 0 and len(flow.nodes) > 1:
        for index in range(2, len(flow.nodes) + 1):
            lines.append(f"    N{index-1:02d} --> N{index:02d}")

    return "\n".join(lines)