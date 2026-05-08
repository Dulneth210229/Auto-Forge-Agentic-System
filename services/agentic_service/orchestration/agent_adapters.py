import inspect
from pathlib import Path
from typing import Any, Dict


async def call_maybe_async(method, **kwargs):
    """
    Calls a method that may be either async or sync.

    Some agents are async because they call Ollama.
    Some older agents are sync.
    This helper supports both.
    """

    result = method(**kwargs)

    if inspect.isawaitable(result):
        return await result

    return result


def normalize_agent_result(result: Any) -> Dict[str, Any]:
    """
    Converts different agent return types into a dictionary.

    Supported:
    - dict
    - Pydantic model
    - string
    - None
    """

    if isinstance(result, dict):
        return result

    if hasattr(result, "model_dump"):
        return result.model_dump()

    if hasattr(result, "dict"):
        return result.dict()

    if isinstance(result, str):
        return {
            "message": result
        }

    if result is None:
        return {
            "message": "Architect Agent completed but returned None."
        }

    return {
        "message": str(result)
    }


def discover_architecture_artifacts(
    run_id: str,
    architecture_version: str,
    output_dir: str = "outputs",
) -> Dict[str, Any]:
    """
    Scans the architecture output folder and discovers generated artifacts.

    This is important because some Architect Agents generate files correctly
    but do not return their file paths.
    """

    architecture_dir = (
        Path(output_dir)
        / "runs"
        / run_id
        / "architecture"
        / architecture_version
    )

    discovered = {
        "artifacts": []
    }

    if not architecture_dir.exists():
        return discovered

    for file_path in architecture_dir.rglob("*"):
        if not file_path.is_file():
            continue

        path_str = str(file_path)

        file_name = file_path.name.lower()
        suffix = file_path.suffix.lower()

        if suffix == ".json" and "sds" in file_name:
            discovered["json_path"] = path_str

        elif suffix == ".md" and "sds" in file_name:
            discovered["markdown_path"] = path_str

        elif suffix == ".yaml" or suffix == ".yml":
            discovered["openapi_yaml_path"] = path_str

        elif suffix == ".json" and "openapi" in file_name:
            discovered["openapi_json_path"] = path_str

        elif suffix in [".puml", ".mmd", ".png", ".pdf", ".jpg", ".jpeg", ".svg"]:
            discovered["artifacts"].append(
                {
                    "type": file_path.stem,
                    "path": path_str
                }
            )

        else:
            discovered["artifacts"].append(
                {
                    "type": suffix.replace(".", "") or "file",
                    "path": path_str
                }
            )

    return discovered


async def call_architect_agent(
    agent: Any,
    run_id: str,
    srs_version: str,
    domain_version: str,
    architecture_version: str,
) -> Dict[str, Any]:
    """
    Calls the Architect Agent using flexible method lookup.

    Supported method names:
    - generate_architecture_pack
    - generate_architecture
    - generate_sds
    - run

    The final result is always normalized into a dictionary.
    """

    candidate_methods = [
        "generate_architecture_pack",
        "generate_architecture",
        "generate_sds",
        "run",
    ]

    for method_name in candidate_methods:
        if hasattr(agent, method_name):
            method = getattr(agent, method_name)

            raw_result = await call_maybe_async(
                method,
                run_id=run_id,
                srs_version=srs_version,
                domain_version=domain_version,
                architecture_version=architecture_version,
            )

            normalized_result = normalize_agent_result(raw_result)

            discovered = discover_architecture_artifacts(
                run_id=run_id,
                architecture_version=architecture_version,
            )

            # Merge discovered paths into the returned result.
            # Existing explicit result values are kept.
            for key, value in discovered.items():
                if key == "artifacts":
                    existing_artifacts = normalized_result.get("artifacts", [])
                    normalized_result["artifacts"] = existing_artifacts + value
                else:
                    normalized_result.setdefault(key, value)

            return normalized_result

    raise AttributeError(
        "ArchitectAgent does not have a supported generation method. "
        "Expected one of: generate_architecture_pack, generate_architecture, generate_sds, run."
    )