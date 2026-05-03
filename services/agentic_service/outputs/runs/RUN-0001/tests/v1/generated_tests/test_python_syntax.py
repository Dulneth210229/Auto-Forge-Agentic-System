import py_compile
from pathlib import Path


TARGET_PATH = Path(r"./sample_ecommerce_app")


def test_python_files_have_valid_syntax():
    """
    Unit-level quality test: all Python files should compile successfully.
    """

    python_files = [
        file_path
        for file_path in TARGET_PATH.rglob("*.py")
        if "venv" not in str(file_path).lower()
        and "__pycache__" not in str(file_path).lower()
    ]

    for python_file in python_files:
        py_compile.compile(str(python_file), doraise=True)
