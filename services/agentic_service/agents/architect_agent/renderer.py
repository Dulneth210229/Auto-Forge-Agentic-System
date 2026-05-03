from pathlib import Path
from jinja2 import Environment, FileSystemLoader

from agents.architect_agent.schemas import SDS, DBPack


def render_sds_markdown(sds: SDS) -> str:
    """
    Renders SDS JSON into readable Markdown.
    """
    env = Environment(
        loader=FileSystemLoader(Path("templates")),
        autoescape=False,
        trim_blocks=True,
        lstrip_blocks=True,
    )

    template = env.get_template("sds.md.j2")
    return template.render(sds=sds)


def render_db_pack_markdown(db_pack: DBPack) -> str:
    """
    Renders DBPack JSON into readable Markdown.
    """
    env = Environment(
        loader=FileSystemLoader(Path("templates")),
        autoescape=False,
        trim_blocks=True,
        lstrip_blocks=True,
    )

    template = env.get_template("db_pack.md.j2")
    return template.render(db=db_pack)