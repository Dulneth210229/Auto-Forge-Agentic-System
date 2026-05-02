from pathlib import Path
from jinja2 import Environment, FileSystemLoader
from agents.domain_agent.schemas import DomainPack


def render_domain_pack_markdown(domain_pack: DomainPack) -> str:
    """
    Converts DomainPack JSON into human-readable Markdown.
    """
    env = Environment(
        loader=FileSystemLoader(Path("templates")),
        autoescape=False,
        trim_blocks=True,
        lstrip_blocks=True
    )

    template = env.get_template("domain_pack.md.j2")
    return template.render(domain=domain_pack)