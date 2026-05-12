import shutil
import subprocess
from pathlib import Path


def render_mermaid_to_png(mmd_path: Path) -> str | None:
    """
    Renders a Mermaid .mmd file into a PNG image using Mermaid CLI.

    Required external tool:
        npm install -g @mermaid-js/mermaid-cli

    Test command:
        mmdc -h

    Returns:
        PNG path as string if successful.
        None if Mermaid CLI is missing or rendering fails.
    """

    mmd_path = Path(mmd_path)

    if not mmd_path.exists():
        print(f"[WARN] Mermaid source file not found: {mmd_path}")
        return None

    content = mmd_path.read_text(encoding="utf-8").strip()

    if not content:
        print(f"[WARN] Mermaid file is empty: {mmd_path}")
        return None

    if "flowchart" not in content and "graph" not in content:
        print(f"[WARN] Mermaid file does not contain a flowchart/graph: {mmd_path}")
        return None

    output_path = mmd_path.with_suffix(".png")

    mmdc_path = shutil.which("mmdc")

    if not mmdc_path:
        print("[WARN] Mermaid CLI (mmdc) not found. Skipping Mermaid PNG export.")
        print("[INFO] Install it using: npm install -g @mermaid-js/mermaid-cli")
        return None

    try:
        subprocess.run(
            [
                mmdc_path,
                "-i", str(mmd_path),
                "-o", str(output_path),
                "-b", "white",
                "-w", "1600",
                "-H", "1200",
            ],
            check=True,
            capture_output=True,
            text=True,
        )

        if output_path.exists() and output_path.stat().st_size > 0:
            return str(output_path)

        print(f"[WARN] Mermaid PNG was not created correctly: {output_path}")
        return None

    except subprocess.CalledProcessError as error:
        print("[WARN] Mermaid render failed.")
        print("[STDOUT]")
        print(error.stdout)
        print("[STDERR]")
        print(error.stderr)
        return None

    except Exception as error:
        print(f"[WARN] Unexpected Mermaid render error: {error}")
        return None


def render_html_to_png(html_path: Path, png_path: Path | None = None) -> str | None:
    """
    Renders a local HTML wireframe into PNG using Playwright.

    Required Python package:
        pip install playwright

    Required browser install:
        python -m playwright install chromium

    Returns:
        PNG path as string if successful.
        None if rendering fails.
    """

    html_path = Path(html_path)

    if png_path is None:
        png_path = html_path.with_suffix(".png")
    else:
        png_path = Path(png_path)

    if not html_path.exists():
        print(f"[WARN] HTML file not found: {html_path}")
        return None

    html_content = html_path.read_text(encoding="utf-8").strip()

    if not html_content:
        print(f"[WARN] HTML file is empty: {html_path}")
        return None

    try:
        from playwright.sync_api import sync_playwright

        html_uri = html_path.resolve().as_uri()

        with sync_playwright() as playwright:
            browser = playwright.chromium.launch(headless=True)

            page = browser.new_page(
                viewport={
                    "width": 1366,
                    "height": 768,
                },
                device_scale_factor=1,
            )

            page.goto(
                html_uri,
                wait_until="networkidle",
                timeout=60000,
            )

            # Small wait helps Tailwind CDN finish applying styles.
            page.wait_for_timeout(1500)

            page.screenshot(
                path=str(png_path),
                full_page=True,
            )

            browser.close()

        if png_path.exists() and png_path.stat().st_size > 0:
            return str(png_path)

        print(f"[WARN] PNG was not created correctly: {png_path}")
        return None

    except ImportError:
        print("[WARN] Playwright is not installed. Skipping HTML to PNG rendering.")
        print("[INFO] Install using: pip install playwright")
        print("[INFO] Then run: python -m playwright install chromium")
        return None

    except Exception as error:
        print(f"[WARN] HTML screenshot render failed for {html_path}: {error}")
        return None


def render_html_folder_to_png(folder_path: Path) -> list[str]:
    """
    Optional helper:
    Renders all .html files inside a folder into PNG files.

    This is useful for manually regenerating screenshots if needed.
    """

    folder_path = Path(folder_path)

    if not folder_path.exists():
        print(f"[WARN] Wireframe folder not found: {folder_path}")
        return []

    rendered_paths = []

    for html_file in folder_path.glob("*.html"):
        png_file = html_file.with_suffix(".png")
        rendered = render_html_to_png(html_file, png_file)

        if rendered:
            rendered_paths.append(rendered)

    return rendered_paths