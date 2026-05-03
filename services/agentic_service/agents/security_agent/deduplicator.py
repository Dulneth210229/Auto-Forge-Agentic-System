from typing import List, Dict, Tuple

from agents.security_agent.schemas import SecurityFinding


class FindingDeduplicator:
    """
    Deduplicates security findings from multiple scanners.

    Why this is needed:
    - AST scanner may detect eval()
    - LLM reviewer may also detect eval()
    - Secret scanner may detect API_KEY
    - LLM reviewer may also detect insecure API key storage

    The goal is not to remove useful findings randomly.
    The goal is to keep the most reliable finding first and remove obvious duplicates.
    """

    DETECTION_PRIORITY = {
        "AST": 1,
        "Dependency": 1,
        "LLM": 2
    }

    KEYWORD_GROUPS = {
        "secret": [
            "secret",
            "api key",
            "apikey",
            "password",
            "token",
            "credential"
        ],
        "eval": [
            "eval",
            "arbitrary code",
            "code execution",
            "untrusted eval"
        ],
        "command_injection": [
            "command injection",
            "subprocess",
            "shell=true",
            "system command"
        ],
        "sql_injection": [
            "sql injection",
            "raw sql",
            "parameterized query",
            "query construction"
        ],
        "xss": [
            "xss",
            "innerhtml",
            "dangerouslysetinnerhtml",
            "cross-site scripting"
        ],
        "cors": [
            "cors",
            "allow_origins",
            "wildcard origin",
            "open redirect"
        ],
        "debug": [
            "debug",
            "stack trace"
        ],
        "weak_hash": [
            "weak hash",
            "md5",
            "sha1",
            "hashing"
        ],
        "local_storage": [
            "localstorage",
            "local storage",
            "token storage",
            "insecure token"
        ]
    }

    def deduplicate(self, findings: List[SecurityFinding]) -> List[SecurityFinding]:
        """
        Deduplicate findings while preserving useful scanner findings.

        Strategy:
        1. Sort by detection priority:
           - AST and Dependency findings are kept first
           - LLM findings are kept if they are unique
        2. Generate a normalized fingerprint for each finding
        3. Skip duplicates with same file + issue category
        4. Reassign stable SEC IDs after deduplication
        """

        sorted_findings = sorted(
            findings,
            key=lambda finding: self.DETECTION_PRIORITY.get(finding.detection_method, 3)
        )

        seen_keys: set[Tuple[str, str]] = set()
        deduplicated: List[SecurityFinding] = []

        for finding in sorted_findings:
            key = self._build_dedup_key(finding)

            if key in seen_keys:
                continue

            seen_keys.add(key)
            deduplicated.append(finding)

        return self._renumber_findings(deduplicated)

    def _build_dedup_key(self, finding: SecurityFinding) -> Tuple[str, str]:
        """
        Build duplicate key using:
        - normalized file path
        - issue category

        This allows AST and LLM findings about the same root issue to collapse.
        """

        file_key = finding.file.replace("\\", "/").lower()
        issue_category = self._classify_issue(finding)

        return file_key, issue_category

    def _classify_issue(self, finding: SecurityFinding) -> str:
        """
        Classify a finding into a high-level issue category.
        """

        text = f"{finding.title} {finding.description} {finding.recommendation}".lower()

        for group_name, keywords in self.KEYWORD_GROUPS.items():
            for keyword in keywords:
                if keyword in text:
                    return group_name

        # Fallback: use CWE if no keyword group matches.
        if finding.cwe and finding.cwe != "N/A":
            return finding.cwe

        # Last fallback: normalized title.
        return finding.title.lower().strip()

    def _renumber_findings(self, findings: List[SecurityFinding]) -> List[SecurityFinding]:
        """
        Reassign SEC IDs after duplicates are removed.

        Example:
        Before:
            SEC-001, SEC-002, SEC-007, SEC-010

        After:
            SEC-001, SEC-002, SEC-003, SEC-004
        """

        for index, finding in enumerate(findings, start=1):
            finding.finding_id = f"SEC-{index:03d}"

        return findings

    def summarize_deduplication(
        self,
        before_count: int,
        after_count: int
    ) -> Dict[str, int]:
        """
        Return a small deduplication summary for CLI output.
        """

        return {
            "findings_before_deduplication": before_count,
            "findings_after_deduplication": after_count,
            "duplicates_removed": before_count - after_count
        }