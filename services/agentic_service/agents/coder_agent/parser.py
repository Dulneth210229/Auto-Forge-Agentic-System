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


def _looks_like_file_path(path: str) -> bool:
    """
    Checks whether a markdown heading looks like a real generated file path.

    This parser stays flexible. MERN-only restrictions should be enforced
    later by patch_policy.py.
    """

    normalized = path.strip().replace("\\", "/")

    common_filenames = {
        "Dockerfile",
        ".gitignore",
        ".dockerignore",
        ".env.example",
        "docker-compose.yml",
        "docker-compose.yaml",
        "README.md",
        "package.json",
        "package-lock.json",
        "yarn.lock",
        "pnpm-lock.yaml",
        "vite.config.js",
        "vite.config.ts",
        "tsconfig.json",
    }

    if normalized in common_filenames:
        return True

    allowed_extensions = (
        ".js",
        ".jsx",
        ".ts",
        ".tsx",
        ".json",
        ".md",
        ".txt",
        ".yml",
        ".yaml",
        ".html",
        ".css",
        ".scss",
        ".env.example",

        # Parser can detect these, but MERN patch policy should reject them.
        ".py",
        ".java",
        ".go",
        ".rb",
        ".php",
        ".cs",
    )

    if normalized.endswith(allowed_extensions):
        return True

    if "/" in normalized and normalized.split("/")[-1] in common_filenames:
        return True

    return False


def parse_file_plan(raw_text: str) -> dict:
    """
    Parse generated files from LLM output.

    Supports:
    1. <file path="backend/server.js">...</file>
    2. [file path="backend/server.js"]...[/file]
    3. [file path="backend/server.js"]: ...
    4. **backend/server.js** ```js ... ```

    The parser does not decide whether a file is allowed.
    patch_policy.py validates that later.
    """

    text = raw_text.strip()
    code_files = {}

    logger.info("LLM output first 500 chars: %s", text[:500])

    # Skip introductory text before first file block.
    first_xml_marker = text.find("<file path=")
    if first_xml_marker != -1 and first_xml_marker > 0:
        logger.info(
            "Found XML file marker at position %s. Skipping preamble.",
            first_xml_marker,
        )
        text = text[first_xml_marker:]

    if "<file path=" not in text:
        first_bracket_marker = text.find("[file path=")
        if first_bracket_marker != -1 and first_bracket_marker > 0:
            logger.info(
                "Found bracket file marker at position %s. Skipping preamble.",
                first_bracket_marker,
            )
            text = text[first_bracket_marker:]

    # Format 1: <file path="...">...</file>
    xml_pattern = re.compile(
        r'<file\s+path=["\']([^"\']+)["\']>\s*(.*?)\s*</file>',
        re.DOTALL | re.IGNORECASE,
    )

    for path, content in xml_pattern.findall(text):
        path = path.strip()
        code_files[path] = _clean_content(content)

    if code_files:
        logger.info("Successfully parsed %s files using XML format", len(code_files))
        return code_files

    # Format 2: [file path="..."]...[/file]
    bracket_pattern = re.compile(
        r'\[file\s+path=["\']([^"\']+)["\']\]\s*(.*?)\s*\[/file\]',
        re.DOTALL | re.IGNORECASE,
    )

    for path, content in bracket_pattern.findall(text):
        path = path.strip()
        code_files[path] = _clean_content(content)

    if code_files:
        logger.info("Successfully parsed %s files using bracket format", len(code_files))
        return code_files

    # Format 3: [file path="..."]: content until next [file path] or end
    bracket_no_close_pattern = re.compile(
        r'\[file\s+path=["\']([^"\']+)["\']\]\:?\s*(.*?)(?=\n\[file\s+path=["\']|\Z)',
        re.DOTALL | re.IGNORECASE,
    )

    for path, content in bracket_no_close_pattern.findall(text):
        path = path.strip()
        content = content.replace("[/file]", "")
        code_files[path] = _clean_content(content)

    if code_files:
        logger.info(
            "Successfully parsed %s files using bracket no-close format",
            len(code_files),
        )
        return code_files

    # Format 4: **filename** ```code```
    markdown_pattern = re.compile(
        r'\*\*([^*]+?)\*\*\s*```(?:[a-zA-Z0-9_+\-\.#]*)?\s*(.*?)```',
        re.DOTALL | re.IGNORECASE,
    )

    for path, content in markdown_pattern.findall(text):
        path = path.strip()

        if _looks_like_file_path(path):
            code_files[path] = _clean_content(content)

    if code_files:
        logger.info("Successfully parsed %s files using markdown format", len(code_files))
        return code_files

    logger.error("Failed to parse LLM output. Raw text length: %s", len(raw_text))
    logger.error("Raw text sample: %s", text[:1000])

    raise CodeFileParseError(
        "Failed to parse LLM output. Expected file blocks such as "
        '<file path="backend/server.js">...</file>.'
    )