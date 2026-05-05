import re


class WireframeParseError(Exception):
    pass


def clean_html_output(raw_output: str) -> str:
    """
    Cleans and validates LLM-generated HTML.

    This function protects the system from common LLM mistakes:
    - markdown fences
    - explanations before/after HTML
    - incomplete HTML
    """

    if not raw_output:
        raise WireframeParseError("LLM output is empty.")

    text = raw_output.strip()

    # Remove markdown fences if the model adds them.
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

    if "<body" not in html.lower():
        raise WireframeParseError("Body tag missing.")

    if "</html>" not in html.lower():
        raise WireframeParseError("Closing HTML tag missing.")

    if "tailwindcss" not in html.lower():
        raise WireframeParseError("Tailwind CDN missing.")

    return html