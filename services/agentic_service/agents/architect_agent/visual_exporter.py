# from pathlib import Path
# import shutil
# import subprocess
# from PIL import Image


# def find_mermaid_command() -> str | None:
#     """
#     Finds the Mermaid CLI command.

#     On Windows, npm global commands are usually available as mmdc.cmd.
#     On macOS/Linux, the command is usually mmdc.
#     """

#     command = shutil.which("mmdc") or shutil.which("mmdc.cmd")

#     return command


# def is_mermaid_cli_available() -> bool:
#     """
#     Checks whether Mermaid CLI is available.
#     """
#     return find_mermaid_command() is not None


# def run_mmdc(input_file: Path, output_file: Path) -> bool:
#     """
#     Runs Mermaid CLI safely.

#     Returns True if the export is successful.
#     Returns False if the export fails.

#     Important:
#     This function does not crash the whole Architect Agent.
#     """

#     mmdc_command = find_mermaid_command()

#     if not mmdc_command:
#         print("[WARN] Mermaid CLI not found in PATH.")
#         return False

#     command = [
#         mmdc_command,
#         "-i",
#         str(input_file),
#         "-o",
#         str(output_file),
#         "-b",
#         "white",
#     ]

#     try:
#         result = subprocess.run(
#             command,
#             capture_output=True,
#             text=True,
#             shell=False,
#         )

#         if result.returncode != 0:
#             print(f"[WARN] Mermaid export failed for {input_file.name} -> {output_file.name}")
#             print(result.stderr)
#             return False

#         return True

#     except FileNotFoundError:
#         print(f"[WARN] Mermaid command not found: {mmdc_command}")
#         return False

#     except Exception as error:
#         print(f"[WARN] Mermaid export crashed for {input_file.name}: {error}")
#         return False


# def export_mermaid_to_visuals(mmd_file: Path) -> list[str]:
#     """
#     Converts a Mermaid .mmd file into PNG, PDF, and JPG.

#     Always returns the .mmd path.
#     Adds PNG/PDF/JPG paths only if export succeeds.
#     """

#     exported_paths = [str(mmd_file)]

#     if not is_mermaid_cli_available():
#         print(
#             f"[WARN] Mermaid CLI not found. Skipping PNG/PDF/JPG export for {mmd_file.name}."
#         )
#         return exported_paths

#     png_file = mmd_file.with_suffix(".png")
#     pdf_file = mmd_file.with_suffix(".pdf")
#     jpg_file = mmd_file.with_suffix(".jpg")

#     png_success = run_mmdc(mmd_file, png_file)
#     if png_success and png_file.exists():
#         exported_paths.append(str(png_file))

#     pdf_success = run_mmdc(mmd_file, pdf_file)
#     if pdf_success and pdf_file.exists():
#         exported_paths.append(str(pdf_file))

#     if png_file.exists():
#         try:
#             image = Image.open(png_file).convert("RGB")
#             image.save(jpg_file, "JPEG", quality=95)
#             exported_paths.append(str(jpg_file))
#         except Exception as error:
#             print(f"[WARN] JPG conversion failed for {png_file.name}: {error}")

#     return exported_paths

from pathlib import Path
import os
import shutil
import subprocess
from PIL import Image


def find_mermaid_command() -> str | None:
    """
    Finds Mermaid CLI on Windows/macOS/Linux.

    Windows global npm commands usually exist as:
    C:/Users/<user>/AppData/Roaming/npm/mmdc.cmd

    This function checks:
    1. System PATH
    2. Common npm global folder
    """

    command = shutil.which("mmdc") or shutil.which("mmdc.cmd")

    if command:
        return command

    npm_prefix = os.popen("npm config get prefix").read().strip()

    if npm_prefix:
        possible_cmd = Path(npm_prefix) / "mmdc.cmd"
        possible_plain = Path(npm_prefix) / "mmdc"

        if possible_cmd.exists():
            return str(possible_cmd)

        if possible_plain.exists():
            return str(possible_plain)

    return None


def run_mmdc(input_file: Path, output_file: Path) -> bool:
    """
    Runs Mermaid CLI to export one diagram.

    Returns True if export succeeds.
    Returns False if export fails.

    This function prints useful error logs instead of crashing the API.
    """

    mmdc_command = find_mermaid_command()

    if not mmdc_command:
        print("[WARN] Mermaid CLI command not found.")
        return False

    command = [
        mmdc_command,
        "-i",
        str(input_file.resolve()),
        "-o",
        str(output_file.resolve()),
        "-b",
        "white",
    ]

    print(f"[INFO] Exporting Mermaid diagram: {input_file.name} -> {output_file.name}")
    print(f"[INFO] Command: {' '.join(command)}")

    result = subprocess.run(
        command,
        capture_output=True,
        text=True,
        shell=False,
    )

    if result.returncode != 0:
        print(f"[WARN] Mermaid export failed for {input_file.name}")
        print("[STDOUT]", result.stdout)
        print("[STDERR]", result.stderr)
        return False

    return output_file.exists()


def convert_png_to_jpg(png_file: Path, jpg_file: Path) -> bool:
    """
    Converts PNG diagram to JPG using Pillow.
    """

    if not png_file.exists():
        print(f"[WARN] Cannot create JPG because PNG missing: {png_file}")
        return False

    try:
        image = Image.open(png_file).convert("RGB")
        image.save(jpg_file, "JPEG", quality=95)
        return jpg_file.exists()
    except Exception as error:
        print(f"[WARN] JPG conversion failed: {error}")
        return False


def export_mermaid_to_visuals(mmd_file: Path) -> list[str]:
    """
    Converts one .mmd file into:
    - .png
    - .pdf
    - .jpg

    Always returns the .mmd path.
    Adds image/pdf paths only if generated successfully.
    """

    exported_paths = [str(mmd_file)]

    png_file = mmd_file.with_suffix(".png")
    pdf_file = mmd_file.with_suffix(".pdf")
    jpg_file = mmd_file.with_suffix(".jpg")

    png_success = run_mmdc(mmd_file, png_file)
    if png_success:
        exported_paths.append(str(png_file))

    pdf_success = run_mmdc(mmd_file, pdf_file)
    if pdf_success:
        exported_paths.append(str(pdf_file))

    jpg_success = convert_png_to_jpg(png_file, jpg_file)
    if jpg_success:
        exported_paths.append(str(jpg_file))

    return exported_paths