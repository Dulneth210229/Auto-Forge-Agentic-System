from agents.security_agent.deduplicator import FindingDeduplicator
from agents.security_agent.schemas import SecurityFinding, TraceabilityLink


def make_finding(
    finding_id: str,
    title: str,
    description: str,
    severity: str,
    file: str,
    detection_method: str,
    cwe: str,
    recommendation: str = "Fix the issue."
):
    return SecurityFinding(
        finding_id=finding_id,
        title=title,
        description=description,
        severity=severity,
        file=file,
        line=1,
        detection_method=detection_method,
        cwe=cwe,
        recommendation=recommendation,
        traceability=TraceabilityLink()
    )


def test_deduplicator_removes_ast_llm_duplicate_eval():
    """
    AST and LLM may both detect eval().
    The deduplicator should keep only one finding for the same file/category.
    """

    findings = [
        make_finding(
            finding_id="SEC-001",
            title="Use of eval() detected",
            description="eval can execute arbitrary code.",
            severity="Critical",
            file="sample_ecommerce_app/app.py",
            detection_method="AST",
            cwe="CWE-95"
        ),
        make_finding(
            finding_id="SEC-002",
            title="Arbitrary Code Execution in dangerous_code endpoint",
            description="The endpoint uses eval() and can execute arbitrary code.",
            severity="Critical",
            file="sample_ecommerce_app/app.py",
            detection_method="LLM",
            cwe="CWE-94"
        )
    ]

    deduplicator = FindingDeduplicator()
    result = deduplicator.deduplicate(findings)

    assert len(result) == 1
    assert result[0].detection_method == "AST"
    assert result[0].finding_id == "SEC-001"


def test_deduplicator_keeps_unique_findings():
    """
    Different issue categories in the same file should be kept.
    """

    findings = [
        make_finding(
            finding_id="SEC-001",
            title="Use of eval() detected",
            description="eval can execute arbitrary code.",
            severity="Critical",
            file="sample_ecommerce_app/app.py",
            detection_method="AST",
            cwe="CWE-95"
        ),
        make_finding(
            finding_id="SEC-002",
            title="Hardcoded secret detected",
            description="API key is hardcoded.",
            severity="High",
            file="sample_ecommerce_app/app.py",
            detection_method="AST",
            cwe="CWE-798"
        )
    ]

    deduplicator = FindingDeduplicator()
    result = deduplicator.deduplicate(findings)

    assert len(result) == 2


def test_deduplicator_renumbers_findings_after_removal():
    """
    After duplicates are removed, SEC IDs should be sequential.
    """

    findings = [
        make_finding(
            finding_id="SEC-001",
            title="Hardcoded secret detected",
            description="API key is hardcoded.",
            severity="High",
            file="app.py",
            detection_method="AST",
            cwe="CWE-798"
        ),
        make_finding(
            finding_id="SEC-005",
            title="SQL Injection",
            description="Raw SQL query.",
            severity="Critical",
            file="app.py",
            detection_method="AST",
            cwe="CWE-89"
        )
    ]

    deduplicator = FindingDeduplicator()
    result = deduplicator.deduplicate(findings)

    assert result[0].finding_id == "SEC-001"
    assert result[1].finding_id == "SEC-002"