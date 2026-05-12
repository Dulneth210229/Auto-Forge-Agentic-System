import pathlib


ALLOWED_FILE_EXTENSIONS = {
    ".py",
    ".txt",
    ".md",
    ".json",
    ".html",
    ".css",
    ".js",
    ".jsx",
    ".ts",
    ".tsx",
    ".yml",
    ".yaml",
    ".go",
    ".rs",
    ".java",
    ".rb",
    ".php",
    ".c",
    ".cpp",
    ".h",
    ".sh",
    ".bash",
}


ALLOWED_FILENAMES = {
    "Dockerfile",
    ".gitignore",
    ".dockerignore",
    "docker-compose.yml",
    "docker-compose.yaml",
    ".env.example",
    "package.json",
    "package-lock.json",
    "yarn.lock",
    "pnpm-lock.yaml",
    "README.md",
    "vite.config.js",
    "vite.config.ts",
}


BLOCKED_PATH_PARTS = {
    ".git",
    ".env",
    ".venv",
    "venv",
    "__pycache__",
    "node_modules",
    "dist",
    "build",
    "target",
    "bin",
    "obj",
}


MERN_ALLOWED_EXTENSIONS = {
    ".js",
    ".jsx",
    ".ts",
    ".tsx",
    ".json",
    ".md",
    ".txt",
    ".yml",
    ".yaml",
    ".css",
    ".html",
}


MERN_ALLOWED_FILENAMES = {
    "Dockerfile",
    ".gitignore",
    ".dockerignore",
    "docker-compose.yml",
    "docker-compose.yaml",
    ".env.example",
    "package.json",
    "package-lock.json",
    "yarn.lock",
    "pnpm-lock.yaml",
    "README.md",
    "vite.config.js",
    "vite.config.ts",
}


def is_safe_generated_path(path: str, tech_stack: str = "generic") -> bool:
    """
    Check if the provided path is safe to generate.

    For MERN mode, only MERN-safe files are allowed.
    """

    p = pathlib.Path(path)

    if p.is_absolute():
        return False

    if ".." in p.parts:
        return False

    for part in p.parts:
        if part in BLOCKED_PATH_PARTS:
            return False

    if tech_stack.lower() == "mern":
        if p.name in MERN_ALLOWED_FILENAMES:
            return True

        if p.suffix in MERN_ALLOWED_EXTENSIONS:
            return True

        return False

    if p.name in ALLOWED_FILENAMES:
        return True

    if p.suffix in ALLOWED_FILE_EXTENSIONS:
        return True

    return False