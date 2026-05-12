import re
from pathlib import Path
from typing import Optional


class VersionManager:
    """
    Handles version numbers such as:

    v1, v2, v3...

    Each stage has independent versions:
    - requirements can be v2
    - domain can still be v1
    """

    VERSION_PATTERN = re.compile(r"^v(\d+)$")

    @staticmethod
    def parse_version(version: str) -> int:
        """
        Converts v1 -> 1, v2 -> 2.

        Raises ValueError for invalid formats.
        """

        match = VersionManager.VERSION_PATTERN.match(version)

        if not match:
            raise ValueError(f"Invalid version format: {version}. Expected format like v1, v2.")

        return int(match.group(1))

    @staticmethod
    def next_version(current_version: Optional[str]) -> str:
        """
        Returns the next version string.

        None -> v1
        v1   -> v2
        v2   -> v3
        """

        if current_version is None:
            return "v1"

        number = VersionManager.parse_version(current_version)
        return f"v{number + 1}"

    @staticmethod
    def find_latest_version(stage_dir: Path) -> Optional[str]:
        """
        Finds the latest version folder inside a stage directory.

        Example:
        outputs/runs/RUN-0001/srs/v1
        outputs/runs/RUN-0001/srs/v2

        returns: v2
        """

        if not stage_dir.exists():
            return None

        versions = []

        for item in stage_dir.iterdir():
            if item.is_dir() and VersionManager.VERSION_PATTERN.match(item.name):
                versions.append(item.name)

        if not versions:
            return None

        versions.sort(key=VersionManager.parse_version)
        return versions[-1]