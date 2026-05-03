from agents.security_agent.gate import SecurityGateEvaluator
from agents.security_agent.schemas import SecurityFinding, TraceabilityLink


def make_finding(
    finding_id: str,
    severity: str,
    title: str = "Test finding"
):
    return SecurityFinding(
        finding_id=finding_id,
        title=title,
        description="Test description",
        severity=severity,
        file="app.py",
        line=1,
        detection_method="AST",
        cwe="CWE-TEST",
        recommendation="Fix issue",
        traceability=TraceabilityLink()
    )


def test_security_gate_fails_when_critical_exists():
    evaluator = SecurityGateEvaluator()

    findings = [
        make_finding("SEC-001", "Critical")
    ]

    decision = evaluator.evaluate(findings)

    assert decision.status == "FAIL"
    assert "Critical" in decision.reason
    assert "SEC-001" in decision.blocking_findings


def test_security_gate_fails_when_too_many_high_findings():
    evaluator = SecurityGateEvaluator()

    findings = [
        make_finding("SEC-001", "High"),
        make_finding("SEC-002", "High"),
        make_finding("SEC-003", "High")
    ]

    decision = evaluator.evaluate(findings)

    assert decision.status == "FAIL"
    assert "High severity findings exceeded" in decision.reason
    assert len(decision.blocking_findings) == 3


def test_security_gate_warns_when_high_within_threshold():
    evaluator = SecurityGateEvaluator()

    findings = [
        make_finding("SEC-001", "High")
    ]

    decision = evaluator.evaluate(findings)

    assert decision.status == "WARN"
    assert "High severity findings exist" in decision.reason


def test_security_gate_warns_when_medium_exists():
    evaluator = SecurityGateEvaluator()

    findings = [
        make_finding("SEC-001", "Medium")
    ]

    decision = evaluator.evaluate(findings)

    assert decision.status == "WARN"
    assert "Medium severity findings" in decision.reason


def test_security_gate_passes_when_only_low_or_no_findings():
    evaluator = SecurityGateEvaluator()

    findings = [
        make_finding("SEC-001", "Low")
    ]

    decision = evaluator.evaluate(findings)

    assert decision.status == "PASS"