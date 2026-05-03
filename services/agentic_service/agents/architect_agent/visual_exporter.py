from pathlib import Path
import subprocess
from PIL import Image


def is_mermaid_cli_available() -> bool:
    """
    Checks whether Mermaid CLI is installed.

    Required command:
    mmdc --version
    """
    try:
        result = subprocess.run(
            ["mmdc", "--version"],
            capture_output=True,
            text=True,
            shell=True,
        )
        return result.returncode == 0
    except Exception:
        return False


def export_mermaid_to_visuals(mmd_file: Path) -> list[str]:
    """
    Converts a .mmd Mermaid file into PNG, PDF, and JPG.

    PNG/PDF are generated using Mermaid CLI.
    JPG is generated from PNG using Pillow.

    If Mermaid CLI is not installed, this function does not crash.
    It simply returns the .mmd file path.
    """
    exported_paths = [str(mmd_file)]

    if not is_mermaid_cli_available():
        print(
            f"[WARN] Mermaid CLI not found. Skipping PNG/PDF/JPG export for {mmd_file.name}."
        )
        return exported_paths

    png_file = mmd_file.with_suffix(".png")
    pdf_file = mmd_file.with_suffix(".pdf")
    jpg_file = mmd_file.with_suffix(".jpg")

    # Export PNG
    subprocess.run(
        [
            "mmdc",
            "-i",
            str(mmd_file),
            "-o",
            str(png_file),
            "-b",
            "white",
        ],
        check=True,
        shell=True,
    )

    exported_paths.append(str(png_file))

    # Export PDF
    subprocess.run(
        [
            "mmdc",
            "-i",
            str(mmd_file),
            "-o",
            str(pdf_file),
            "-b",
            "white",
        ],
        check=True,
        shell=True,
    )

    exported_paths.append(str(pdf_file))

    # Convert PNG to JPG using Pillow
    if png_file.exists():
        image = Image.open(png_file).convert("RGB")
        image.save(jpg_file, "JPEG", quality=95)
        exported_paths.append(str(jpg_file))

    return exported_paths