from agents.security_agent.scanners.base import FindingFactory
from agents.security_agent.scanners.python_ast_scanner import PythonASTScanner
from agents.security_agent.scanners.multi_scanner import MultiSecurityScanner


class ASTSecurityScanner(PythonASTScanner):
    """
    Backward-compatible wrapper.

    Older tests may import ASTSecurityScanner from:
    agents.security_agent.scanner

    Internally, we now use PythonASTScanner from:
    agents.security_agent.scanners.python_ast_scanner
    """

    def __init__(self):
        super().__init__(FindingFactory())