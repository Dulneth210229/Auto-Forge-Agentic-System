from pathlib import Path

from jinja2 import Environment, FileSystemLoader, select_autoescape

from agents.tester_agent.schemas import TestReport


def render_test_report_markdown(report: TestReport) -> str:
    """
    Render TestReport JSON data into human-readable Markdown.
    """

    templates_dir = Path("templates")

    env = Environment(
        loader=FileSystemLoader(str(templates_dir)),
        autoescape=select_autoescape()
    )

    template = env.get_template("test_report.md.j2")

    return template.render(report=report)