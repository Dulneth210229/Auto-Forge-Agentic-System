from agents.uiux_agent.schemas import UserFlow


def build_mermaid_from_flow(flow: UserFlow) -> str:
    """
    Converts an LLM-generated UserFlow object into Mermaid syntax.

    Important:
    This file does NOT decide screens.
    This file does NOT hardcode user journeys.
    It only renders the flow that the LLM already generated.
    """

    lines = ["flowchart TD"]

    for node in flow.nodes:
        label = node.label

        if node.screen_id:
            label = f"{node.screen_id} {node.label}"

        safe_label = label.replace('"', "'")

        if node.id.lower().endswith("start") or node.label.lower() == "start":
            lines.append(f'    {node.id}(["{safe_label}"])')
        else:
            lines.append(f'    {node.id}["{safe_label}"]')

    lines.append("")

    for edge in flow.edges:
        if edge.condition:
            condition = edge.condition.replace('"', "'")
            lines.append(f'    {edge.from_node} -->|"{condition}"| {edge.to_node}')
        else:
            lines.append(f"    {edge.from_node} --> {edge.to_node}")

    return "\n".join(lines)