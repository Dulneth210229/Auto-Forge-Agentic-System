from pathlib import Path
from jinja2 import Environment, FileSystemLoader
from agents.requirement_agent.schemas import SRS


def render_srs_markdown(srs: SRS) -> str:
    template_dir = Path("templates")

    env = Environment(
        loader=FileSystemLoader(template_dir),
        autoescape=False,
        trim_blocks=True,
        lstrip_blocks=True
    )

    template = env.get_template("srs.md.j2")
    return template.render(srs=srs)