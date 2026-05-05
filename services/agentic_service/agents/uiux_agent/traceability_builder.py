from agents.uiux_agent.schemas import UIScreen, UITraceLink


def build_ui_traceability(screens: list[UIScreen]) -> list[UITraceLink]:
    """
    Builds FR -> UI screen traceability.
    """

    links = []

    for screen in screens:
        for requirement_id in screen.related_requirements:
            links.append(
                UITraceLink(
                    requirement_id=requirement_id,
                    screen_id=screen.id,
                    screen_name=screen.name,
                    reason=f"{screen.name} screen supports requirement {requirement_id}.",
                )
            )

    return links