import pathlib

ALLOWED_FILE_EXTENSIONS = {
    ".py", ".txt", ".md", ".json", ".html",
    ".css", ".js", ".yml", ".yaml", ".gitignore"
}

BLOCKED_PATH_PARTS = {
    ".git", "venv", "__pycache__", "node_modules", ".env"
}

def is_safe_generated_path(path: str) -> bool:
    """Check if the provided path is safe to generate."""
    p = pathlib.Path(path)
    
    # Check if any part of the path is blocked
    for part in p.parts:
        if part in BLOCKED_PATH_PARTS:
            return False
            
    # Allow .gitignore despite it being an extension without a name
    if p.name == ".gitignore":
        return True
        
    # Check if extension is allowed
    if p.suffix not in ALLOWED_FILE_EXTENSIONS:
        return False
        
    return True
