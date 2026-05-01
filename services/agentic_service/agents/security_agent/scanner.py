import ast
import re
from pathlib import Path
from typing import List

from agents.security_agent.schemas import SecurityFinding, TraceabilityLink


class ASTSecurityScanner:
    """
    AST-based static security scanner for Python source code.

    This scanner detects basic insecure coding patterns such as:
    - Hardcoded secrets
    - eval() / exec()
    - unsafe subprocess usage
    - debug=True
    - weak hashing algorithms
    - raw SQL string formatting

    This is a lightweight custom SAST scanner for the Security Agent MVP.
    """

    def __init__(self):
        self.finding_counter = 1

    def scan_directory(self, target_path: str) -> List[SecurityFinding]:
        """
        Scan all Python files inside the given target directory.

        Args:
            target_path: Folder path containing Python source files.

        Returns:
            List of SecurityFinding objects.
        """

        target = Path(target_path)

        if not target.exists():
            raise FileNotFoundError(f"Target path does not exist: {target_path}")

        findings: List[SecurityFinding] = []

        for py_file in target.rglob("*.py"):
            findings.extend(self.scan_file(py_file))

        return findings

    def scan_file(self, file_path: Path) -> List[SecurityFinding]:
        """
        Scan a single Python file using AST and line-based checks.
        """

        findings: List[SecurityFinding] = []

        try:
            source_code = file_path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            source_code = file_path.read_text(encoding="latin-1")

        try:
            tree = ast.parse(source_code)
        except SyntaxError:
            findings.append(
                self._create_finding(
                    title="Python syntax error",
                    description="The file could not be parsed by the AST scanner due to a syntax error.",
                    severity="Low",
                    file=str(file_path),
                    line=0,
                    cwe="N/A",
                    recommendation="Fix syntax errors so that static analysis can scan the file correctly."
                )
            )
            return findings

        findings.extend(self._detect_ast_issues(tree, file_path))
        findings.extend(self._detect_line_based_issues(source_code, file_path))

        return findings

    def _detect_ast_issues(self, tree: ast.AST, file_path: Path) -> List[SecurityFinding]:
        """
        Detect issues using Python AST nodes.
        """

        findings: List[SecurityFinding] = []

        for node in ast.walk(tree):
            # Detect eval() and exec()
            if isinstance(node, ast.Call):
                function_name = self._get_call_name(node)

                if function_name == "eval":
                    findings.append(
                        self._create_finding(
                            title="Use of eval() detected",
                            description="The eval() function can execute arbitrary code and may lead to remote code execution.",
                            severity="Critical",
                            file=str(file_path),
                            line=getattr(node, "lineno", 0),
                            cwe="CWE-95",
                            recommendation="Avoid eval(). Use safe parsing or explicit logic instead."
                        )
                    )

                if function_name == "exec":
                    findings.append(
                        self._create_finding(
                            title="Use of exec() detected",
                            description="The exec() function can execute arbitrary Python code and is dangerous with user-controlled input.",
                            severity="Critical",
                            file=str(file_path),
                            line=getattr(node, "lineno", 0),
                            cwe="CWE-94",
                            recommendation="Avoid exec(). Replace it with safe, controlled function calls."
                        )
                    )

                # Detect subprocess with shell=True
                if function_name in ["subprocess.call", "subprocess.run", "subprocess.Popen"]:
                    for keyword in node.keywords:
                        if keyword.arg == "shell" and isinstance(keyword.value, ast.Constant):
                            if keyword.value.value is True:
                                findings.append(
                                    self._create_finding(
                                        title="Unsafe subprocess usage with shell=True",
                                        description="Using subprocess with shell=True may allow command injection.",
                                        severity="High",
                                        file=str(file_path),
                                        line=getattr(node, "lineno", 0),
                                        cwe="CWE-78",
                                        recommendation="Use shell=False and pass command arguments as a list."
                                    )
                                )

                # Detect weak hashing algorithms
                if function_name in ["hashlib.md5", "hashlib.sha1"]:
                    findings.append(
                        self._create_finding(
                            title="Weak hashing algorithm detected",
                            description=f"The code uses {function_name}, which is considered weak for security-sensitive hashing.",
                            severity="Medium",
                            file=str(file_path),
                            line=getattr(node, "lineno", 0),
                            cwe="CWE-327",
                            recommendation="Use SHA-256, SHA-512, bcrypt, Argon2, or another secure hashing approach depending on the use case."
                        )
                    )

            # Detect hardcoded secrets in assignments
            if isinstance(node, ast.Assign):
                findings.extend(self._detect_hardcoded_secret(node, file_path))

        return findings

    def _detect_line_based_issues(self, source_code: str, file_path: Path) -> List[SecurityFinding]:
        """
        Detect issues that are easier to identify using line-based checks.
        """

        findings: List[SecurityFinding] = []
        lines = source_code.splitlines()

        sql_format_patterns = [
            r"SELECT\s+.*\+",
            r"INSERT\s+.*\+",
            r"UPDATE\s+.*\+",
            r"DELETE\s+.*\+",
            r"SELECT\s+.*%",
            r"INSERT\s+.*%",
            r"UPDATE\s+.*%",
            r"DELETE\s+.*%",
            r"SELECT\s+.*\.format",
            r"INSERT\s+.*\.format",
            r"UPDATE\s+.*\.format",
            r"DELETE\s+.*\.format",
            r"f[\"'].*SELECT\s+",
            r"f[\"'].*INSERT\s+",
            r"f[\"'].*UPDATE\s+",
            r"f[\"'].*DELETE\s+"
        ]

        for line_number, line in enumerate(lines, start=1):
            normalized_line = line.strip()

            # Detect debug=True
            if re.search(r"debug\s*=\s*True", normalized_line):
                findings.append(
                    self._create_finding(
                        title="Debug mode enabled",
                        description="Debug mode may expose sensitive stack traces and internal application information.",
                        severity="Medium",
                        file=str(file_path),
                        line=line_number,
                        cwe="CWE-489",
                        recommendation="Disable debug mode in production environments."
                    )
                )

            # Detect insecure CORS wildcard
            if "allow_origins" in normalized_line and "*" in normalized_line:
                findings.append(
                    self._create_finding(
                        title="Insecure CORS wildcard detected",
                        description="Using wildcard CORS origins may allow untrusted websites to interact with the API.",
                        severity="Medium",
                        file=str(file_path),
                        line=line_number,
                        cwe="CWE-942",
                        recommendation="Restrict CORS origins to trusted frontend domains."
                    )
                )

            # Detect raw SQL formatting
            for pattern in sql_format_patterns:
                if re.search(pattern, normalized_line, re.IGNORECASE):
                    findings.append(
                        self._create_finding(
                            title="Possible raw SQL string formatting",
                            description="SQL queries built using string formatting or concatenation may cause SQL injection.",
                            severity="High",
                            file=str(file_path),
                            line=line_number,
                            cwe="CWE-89",
                            recommendation="Use parameterized queries or an ORM query builder."
                        )
                    )
                    break

        return findings

    def _detect_hardcoded_secret(self, node: ast.Assign, file_path: Path) -> List[SecurityFinding]:
        """
        Detect hardcoded secrets assigned to variables.

        Example:
            API_KEY = "abc123"
            password = "admin123"
            SECRET_KEY = "secret"
        """

        findings: List[SecurityFinding] = []

        secret_keywords = [
            "password",
            "passwd",
            "pwd",
            "secret",
            "api_key",
            "apikey",
            "token",
            "access_key",
            "private_key"
        ]

        for target in node.targets:
            if isinstance(target, ast.Name):
                variable_name = target.id.lower()

                if any(keyword in variable_name for keyword in secret_keywords):
                    if isinstance(node.value, ast.Constant) and isinstance(node.value.value, str):
                        if len(node.value.value.strip()) >= 4:
                            findings.append(
                                self._create_finding(
                                    title="Hardcoded secret detected",
                                    description=f"The variable '{target.id}' appears to contain a hardcoded secret.",
                                    severity="High",
                                    file=str(file_path),
                                    line=getattr(node, "lineno", 0),
                                    cwe="CWE-798",
                                    recommendation="Move secrets to environment variables or a secure secret manager."
                                )
                            )

        return findings

    def _get_call_name(self, node: ast.Call) -> str:
        """
        Extract function call name from AST node.

        Examples:
            eval() → eval
            subprocess.run() → subprocess.run
            hashlib.md5() → hashlib.md5
        """

        if isinstance(node.func, ast.Name):
            return node.func.id

        if isinstance(node.func, ast.Attribute):
            parts = []
            current = node.func

            while isinstance(current, ast.Attribute):
                parts.append(current.attr)
                current = current.value

            if isinstance(current, ast.Name):
                parts.append(current.id)

            return ".".join(reversed(parts))

        return ""

    def _create_finding(
        self,
        title: str,
        description: str,
        severity: str,
        file: str,
        line: int,
        cwe: str,
        recommendation: str
    ) -> SecurityFinding:
        """
        Create a SecurityFinding object with stable SEC IDs.
        """

        finding_id = f"SEC-{self.finding_counter:03d}"
        self.finding_counter += 1

        return SecurityFinding(
            finding_id=finding_id,
            title=title,
            description=description,
            severity=severity,
            file=file,
            line=line,
            detection_method="AST",
            cwe=cwe,
            recommendation=recommendation,
            traceability=TraceabilityLink(
                requirement_id="",
                api="",
                module=""
            )
        )