from typing import List

from agents.security_agent.schemas import SecurityFinding, SecurityFixSuggestion


class SecurityFixSuggester:
    """
    Generates structured fix suggestions for security findings.

    This is currently rule-based.

    Later, we can extend it so:
    - LLM improves the fix text
    - Coder Agent uses the fix suggestions to create patches
    - Tool Runner verifies whether the fixes pass tests
    """

    def generate_fix_suggestions(
        self,
        findings: List[SecurityFinding]
    ) -> List[SecurityFixSuggestion]:
        """
        Generate fix suggestions for all findings.
        """

        return [
            self.generate_fix_suggestion(finding)
            for finding in findings
        ]

    def generate_fix_suggestion(
        self,
        finding: SecurityFinding
    ) -> SecurityFixSuggestion:
        """
        Generate one fix suggestion based on CWE, title, and description.
        """

        text = (
            f"{finding.title} "
            f"{finding.description} "
            f"{finding.recommendation} "
            f"{finding.cwe}"
        ).lower()

        recommended_fix, example_fix, effort = self._build_fix_content(text, finding)
        priority = self._priority_from_severity(finding.severity)

        return SecurityFixSuggestion(
            finding_id=finding.finding_id,
            issue=finding.title,
            severity=finding.severity,
            file=finding.file,
            recommended_fix=recommended_fix,
            example_fix=example_fix,
            priority=priority,
            effort=effort
        )

    def _build_fix_content(
        self,
        text: str,
        finding: SecurityFinding
    ) -> tuple[str, str, str]:
        """
        Return:
        - recommended_fix
        - example_fix
        - effort
        """

        if self._contains_any(text, ["secret", "api key", "apikey", "password", "token", "credential", "cwe-798", "cwe-259"]):
            return (
                "Move hardcoded secrets into environment variables or a secure secret manager.",
                "import os\nSECRET_KEY = os.getenv('SECRET_KEY')",
                "Low"
            )

        if self._contains_any(text, ["sql injection", "raw sql", "parameterized", "cwe-89"]):
            return (
                "Replace SQL string concatenation with parameterized queries or ORM-safe query methods.",
                "db.execute('SELECT * FROM products WHERE name = ?', [keyword])",
                "Medium"
            )

        if self._contains_any(text, ["eval", "arbitrary code", "code execution", "cwe-95", "cwe-94"]):
            return (
                "Remove eval/exec usage and replace it with safe parsing or explicit controlled logic.",
                "Use json.loads(user_input) for JSON data instead of eval(user_input).",
                "Medium"
            )

        if self._contains_any(text, ["command injection", "subprocess", "shell=true", "system command", "cwe-78"]):
            return (
                "Avoid shell=True and pass command arguments as a safe list with strict input validation.",
                "subprocess.run(['echo', safe_value], shell=False, check=True)",
                "Medium"
            )

        if self._contains_any(text, ["md5", "sha1", "weak hashing", "cwe-327"]):
            return (
                "Replace weak hashing algorithms with secure hashing suitable for the use case.",
                "hashlib.sha256(value.encode()).hexdigest()",
                "Low"
            )

        if self._contains_any(text, ["cors", "allow_origins", "wildcard", "cwe-942"]):
            return (
                "Restrict CORS origins to trusted frontend domains instead of using wildcards.",
                "allow_origins=['https://your-frontend-domain.com']",
                "Low"
            )

        if self._contains_any(text, ["debug", "stack trace", "cwe-489"]):
            return (
                "Disable debug mode in production and control it through environment configuration.",
                "app = FastAPI(debug=False)",
                "Low"
            )

        if self._contains_any(text, ["innerhtml", "xss", "cross-site scripting", "dangerouslysetinnerhtml", "cwe-79"]):
            return (
                "Avoid rendering unsanitized user input as HTML. Use safe text rendering or sanitize HTML.",
                "element.textContent = userInput;",
                "Medium"
            )

        if self._contains_any(text, ["localstorage", "local storage", "token storage", "cwe-922", "cwe-356"]):
            return (
                "Avoid storing sensitive tokens in localStorage. Prefer secure HttpOnly cookies or server-side sessions.",
                "Set session token in a Secure, HttpOnly, SameSite cookie from the backend.",
                "Medium"
            )

        if self._contains_any(text, ["dependency", "package", "osv", "vulnerable dependency", "cwe-937"]):
            return (
                "Upgrade the vulnerable dependency to a patched and currently supported version.",
                "Update requirements.txt or package.json, then rerun dependency scanning.",
                "Medium"
            )

        if self._contains_any(text, ["docker", "root", "container", "cwe-250"]):
            return (
                "Run the container using a non-root user to reduce the impact of container compromise.",
                "RUN adduser --disabled-password appuser\nUSER appuser",
                "Medium"
            )

        return (
            "Review the finding and apply a secure coding fix based on the recommendation.",
            finding.recommendation,
            "Medium"
        )

    def _priority_from_severity(self, severity: str) -> str:
        """
        Convert severity to remediation priority.
        """

        if severity == "Critical":
            return "Immediate"

        if severity == "High":
            return "High"

        if severity == "Medium":
            return "Normal"

        return "Low"

    def _contains_any(self, text: str, keywords: List[str]) -> bool:
        """
        Check if any keyword appears in text.
        """

        return any(keyword in text for keyword in keywords)