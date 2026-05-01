from pathlib import Path

from agents.security_agent.scanner import ASTSecurityScanner


def test_scanner_detects_hardcoded_secret(tmp_path: Path):
    """
    This test checks whether the scanner can detect a hardcoded secret.
    """

    test_file = tmp_path / "config.py"

    test_file.write_text(
        'API_KEY = "12345-secret-key"\n',
        encoding="utf-8"
    )

    scanner = ASTSecurityScanner()
    findings = scanner.scan_directory(str(tmp_path))

    titles = [finding.title for finding in findings]

    assert "Hardcoded secret detected" in titles


def test_scanner_detects_eval_usage(tmp_path: Path):
    """
    This test checks whether the scanner can detect eval().
    """

    test_file = tmp_path / "danger.py"

    test_file.write_text(
        """
def run_user_code(user_input):
    return eval(user_input)
""",
        encoding="utf-8"
    )

    scanner = ASTSecurityScanner()
    findings = scanner.scan_directory(str(tmp_path))

    titles = [finding.title for finding in findings]

    assert "Use of eval() detected" in titles


def test_scanner_detects_exec_usage(tmp_path: Path):
    """
    This test checks whether the scanner can detect exec().
    """

    test_file = tmp_path / "danger_exec.py"

    test_file.write_text(
        """
def run_code(user_input):
    exec(user_input)
""",
        encoding="utf-8"
    )

    scanner = ASTSecurityScanner()
    findings = scanner.scan_directory(str(tmp_path))

    titles = [finding.title for finding in findings]

    assert "Use of exec() detected" in titles


def test_scanner_detects_subprocess_shell_true(tmp_path: Path):
    """
    This test checks whether the scanner can detect subprocess shell=True.
    """

    test_file = tmp_path / "commands.py"

    test_file.write_text(
        """
import subprocess

def run_command(command):
    subprocess.run(command, shell=True)
""",
        encoding="utf-8"
    )

    scanner = ASTSecurityScanner()
    findings = scanner.scan_directory(str(tmp_path))

    titles = [finding.title for finding in findings]

    assert "Unsafe subprocess usage with shell=True" in titles


def test_scanner_detects_weak_hashing(tmp_path: Path):
    """
    This test checks whether the scanner can detect weak hashing.
    """

    test_file = tmp_path / "hashing.py"

    test_file.write_text(
        """
import hashlib

def hash_value(value):
    return hashlib.md5(value.encode()).hexdigest()
""",
        encoding="utf-8"
    )

    scanner = ASTSecurityScanner()
    findings = scanner.scan_directory(str(tmp_path))

    titles = [finding.title for finding in findings]

    assert "Weak hashing algorithm detected" in titles