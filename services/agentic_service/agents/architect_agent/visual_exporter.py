from pathlib import Path
import os
import shutil
import subprocess


def find_java() -> str | None:
    """
    Finds Java executable in system PATH.
    """
    return shutil.which("java")


def find_graphviz_dot() -> str | None:
    """
    Finds Graphviz dot executable in system PATH.
    """
    return shutil.which("dot")


def find_plantuml_jar() -> Path | None:
    """
    Finds PlantUML jar from a known project location.

    Expected default location:
    tools/plantuml/plantuml.jar
    """
    candidate = Path("tools") / "plantuml" / "plantuml.jar"

    if candidate.exists():
        return candidate.resolve()

    return None


def is_plantuml_ready() -> tuple[bool, list[str]]:
    """
    Checks whether Java, Graphviz, and PlantUML jar are ready.
    """
    issues = []

    if not find_java():
        issues.append("Java not found in PATH.")

    if not find_graphviz_dot():
        issues.append("Graphviz 'dot' not found in PATH.")

    if not find_plantuml_jar():
        issues.append("PlantUML jar not found at tools/plantuml/plantuml.jar")

    return len(issues) == 0, issues


def export_puml_to_png(puml_file: Path) -> list[str]:
    """
    Converts one .puml diagram into PNG using PlantUML.

    Output:
        same folder / same base filename .png

    Returns list of successfully generated file paths.
    """
    exported = [str(puml_file)]

    ready, issues = is_plantuml_ready()

    if not ready:
        print("[WARN] PlantUML export skipped.")
        for issue in issues:
            print(f"[WARN] {issue}")
        return exported

    java_cmd = find_java()
    plantuml_jar = find_plantuml_jar()

    command = [
        java_cmd,
        "-jar",
        str(plantuml_jar),
        "-tpng",
        str(puml_file.resolve()),
    ]

    print(f"[INFO] Running PlantUML export for: {puml_file.name}")
    print(f"[INFO] Command: {' '.join(command)}")

    result = subprocess.run(
        command,
        capture_output=True,
        text=True,
        shell=False,
    )

    if result.returncode != 0:
        print(f"[WARN] PlantUML export failed for {puml_file.name}")
        print("[STDOUT]", result.stdout)
        print("[STDERR]", result.stderr)
        return exported

    png_file = puml_file.with_suffix(".png")

    if png_file.exists():
        exported.append(str(png_file))

    return exported