from pathlib import Path


TARGET_PATH = Path(r"./sample_ecommerce_app")


def test_target_project_folder_exists():
    """
    Smoke test: target generated project folder should exist.
    """

    assert TARGET_PATH.exists(), f"Target project folder does not exist: {TARGET_PATH}"


def test_target_project_contains_source_files():
    """
    Smoke test: generated project should contain at least one source file.
    """

    source_extensions = [".py", ".js", ".jsx", ".ts", ".tsx"]

    source_files = [
        file_path
        for file_path in TARGET_PATH.rglob("*")
        if file_path.is_file() and file_path.suffix.lower() in source_extensions
    ]

    assert source_files, "No Python/JavaScript/TypeScript source files were found."


def test_target_project_has_ecommerce_related_files_or_content():
    """
    Smoke test: project should contain at least some e-commerce related content.
    """

    keywords = ["product", "catalog", "cart", "checkout", "order"]

    combined_text = ""

    for file_path in TARGET_PATH.rglob("*"):
        if file_path.is_file() and file_path.suffix.lower() in [".py", ".js", ".jsx", ".ts", ".tsx", ".json"]:
            try:
                combined_text += file_path.read_text(encoding="utf-8").lower()
            except UnicodeDecodeError:
                continue

    assert any(keyword in combined_text for keyword in keywords), (
        "No e-commerce related keywords were found in the generated project."
    )
