from pathlib import Path
import shutil
import subprocess
from playwright.sync_api import sync_playwright


def render_mermaid_to_png(mmd_path: Path) -> str | None:
    """
    Converts Mermaid .mmd file into PNG using Mermaid CLI.

    If Mermaid CLI is not installed, returns None without crashing.
    """

    command = shutil.which("mmdc") or shutil.which("mmdc.cmd")

    if not command:
        print("[WARN] Mermaid CLI not found. Skipping flow PNG rendering.")
        return None

    png_path = mmd_path.with_suffix(".png")

    result = subprocess.run(
        [
            command,
            "-i",
            str(mmd_path.resolve()),
            "-o",
            str(png_path.resolve()),
            "-b",
            "white",
        ],
        capture_output=True,
        text=True,
        shell=False,
    )

    if result.returncode != 0:
        print("[WARN] Mermaid rendering failed.")
        print(result.stderr)
        return None

    return str(png_path) if png_path.exists() else None


def render_html_to_png(html_path: Path, png_path: Path) -> str | None:
    """
    Opens an HTML wireframe in Chromium and captures a PNG screenshot.

    This gives human-readable UI/UX artifacts from generated HTML.
    """

    try:
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch(headless=True)
            page = browser.new_page(viewport={"width": 1366, "height": 768})
            page.goto(html_path.resolve().as_uri())
            page.screenshot(path=str(png_path.resolve()), full_page=True)
            browser.close()

        return str(png_path) if png_path.exists() else None

    except Exception as error:
        print(f"[WARN] Playwright screenshot failed for {html_path.name}: {error}")
        return None