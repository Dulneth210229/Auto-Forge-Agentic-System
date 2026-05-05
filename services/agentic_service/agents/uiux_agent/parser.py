import json
import re

from agents.uiux_agent.schemas import (
    UIScreen,
    UserFlow,
    UITraceLink,
)


class UIUXParseError(Exception):
    pass


class WireframeParseError(Exception):
    pass


def extract_json_object(raw_output: str) -> dict:
    """
    Extracts a JSON object from LLM output.

    The LLM should return JSON only, but this safely handles accidental text.
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

    json_text = text[start:end + 1]

    try:
        return json.loads(json_text)
    except json.JSONDecodeError as error:
        raise UIUXParseError(f"Invalid JSON from LLM: {error}") from error


def parse_uiux_plan(raw_output: str) -> tuple[list[UIScreen], list[UserFlow], list[UITraceLink]]:
    """
    Parses and validates the LLM-generated UI/UX plan.
    """

    data = extract_json_object(raw_output)

    if "screens" not in data:
        raise UIUXParseError("UI/UX plan missing 'screens'.")

    if "user_flows" not in data:
        raise UIUXParseError("UI/UX plan missing 'user_flows'.")

    if "traceability" not in data:
        raise UIUXParseError("UI/UX plan missing 'traceability'.")

    screens = [UIScreen.model_validate(item) for item in data["screens"]]
    user_flows = [UserFlow.model_validate(item) for item in data["user_flows"]]
    traceability = [UITraceLink.model_validate(item) for item in data["traceability"]]

    if not screens:
        raise UIUXParseError("LLM returned zero UI screens.")

    if not user_flows:
        raise UIUXParseError("LLM returned zero user flows.")

    return screens, user_flows, traceability


def clean_html_output(raw_output: str) -> str:
    """
    Validates LLM-generated high-fidelity HTML.

    This does NOT create fallback UI.
    It only cleans markdown fences and validates completeness.
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

    if html_start == -1 or html_end == -1:
        raise WireframeParseError("LLM output does not contain complete HTML.")

    html = text[html_start:html_end + len("</html>")]

    if "<html" not in html.lower():
        raise WireframeParseError("HTML tag missing.")

    if "<head" not in html.lower():
        raise WireframeParseError("Head tag missing.")

    if "<body" not in html.lower():
        raise WireframeParseError("Body tag missing.")

    if "</html>" not in html.lower():
        raise WireframeParseError("Closing HTML tag missing.")

    if "tailwindcss" not in html.lower():
        raise WireframeParseError("Tailwind CDN missing.")

    return html