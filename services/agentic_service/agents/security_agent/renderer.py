from pathlib import Path
from jinja2 import Environment, FileSystemLoader
from agents.security_agent.schemas import SecurityReport


def render_security_report_markdown(report: SecurityReport) -> str:
    """
    Converts SecurityReport JSON data into a human-readable Markdown report.

    Input:
        SecurityReport Pydantic object

    Output:
        Markdown string
    """

    template_dir = Path("templates")

    env = Environment(
        loader=FileSystemLoader(template_dir),
        autoescape=False,
        trim_blocks=True,
        lstrip_blocks=True
    )

    template = env.get_template("security_report.md.j2")

    return template.render(report=report)