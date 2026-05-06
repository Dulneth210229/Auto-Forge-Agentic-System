import re
import logging

logger = logging.getLogger(__name__)


class CodeFileParseError(Exception):
    pass


def _clean_content(content: str) -> str:
    """
    Removes unnecessary markdown code fences from generated file content.
    """
    content = content.strip()

    if content.startswith("```"):
        lines = content.splitlines()
        if lines:
            lines = lines[1:]
        content = "\n".join(lines)

    if content.endswith("```"):
        lines = content.splitlines()
        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]
        content = "\n".join(lines)

    return content.strip()


def parse_file_plan(raw_text: str) -> dict:
    """
    Parse generated files from LLM output.

    Supports:
    1. <file path="backend/main.py">...</file>
    2. [file path="backend/main.py"]...[/file]
    3. [file path="backend/main.py"]: ...
    4. **backend/main.py** ```python ... ```
    """

    text = raw_text.strip()
    code_files = {}

    # Log the first 500 chars to debug what we're receiving
    logger.info(f"LLM output (first 500 chars): {text[:500]}")

    # Format 1: <file path="...">...</file>
    xml_pattern = re.compile(
        r'<file\s+path="([^"]+)">\s*(.*?)\s*</file>',
        re.DOTALL | re.IGNORECASE
    )

    for path, content in xml_pattern.findall(text):
        logger.debug(f"Found XML format file: {path}")
        code_files[path.strip()] = _clean_content(content)

    if code_files:
        logger.info(f"Successfully parsed {len(code_files)} files using XML format")
        return code_files

    # Format 2: [file path="..."]...[/file]
    bracket_pattern = re.compile(
        r'\[file\s+path="([^"]+)"\]\s*(.*?)\s*\[/file\]',
        re.DOTALL | re.IGNORECASE
    )

    for path, content in bracket_pattern.findall(text):
        logger.debug(f"Found bracket format file: {path}")
        code_files[path.strip()] = _clean_content(content)

    if code_files:
        logger.info(f"Successfully parsed {len(code_files)} files using bracket format")
        return code_files

    # Format 3: [file path="..."]: content until next [file path] or end
    bracket_no_close_pattern = re.compile(
        r'\[file\s+path="([^"]+)"\]\:?\s*(.*?)(?=\n\[file\s+path="|\Z)',
        re.DOTALL | re.IGNORECASE
    )

    for path, content in bracket_no_close_pattern.findall(text):
        logger.debug(f"Found bracket no-close format file: {path}")
        content = content.replace("[/file]", "")
        code_files[path.strip()] = _clean_content(content)

    if code_files:
        logger.info(f"Successfully parsed {len(code_files)} files using bracket no-close format")
        return code_files

    # Format 4: **filename** ```code```
    markdown_pattern = re.compile(
        r'\*\*([^*]+\.(?:py|html|css|js|json|md|txt|yml|yaml|gitignore|Dockerfile))\*\*\s*```(?:[a-zA-Z0-9_-]+)?\s*(.*?)```',
        re.DOTALL | re.IGNORECASE
    )

    for path, content in markdown_pattern.findall(text):
        logger.debug(f"Found markdown format file: {path}")
        code_files[path.strip()] = _clean_content(content)

    if code_files:
        logger.info(f"Successfully parsed {len(code_files)} files using markdown format")
        return code_files

    logger.error(f"Failed to parse LLM output. Raw text length: {len(raw_text)}")
    logger.error(f"Raw text sample: {text[:1000]}")
    raise CodeFileParseError(
        "Failed to parse LLM output. Expected file blocks such as "
        '<file path="backend/main.py">...</file> or '
        '[file path="backend/main.py"]...[/file].'
    )