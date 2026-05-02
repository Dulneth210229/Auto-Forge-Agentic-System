from agents.security_agent.fix_suggester import SecurityFixSuggester
from agents.security_agent.schemas import SecurityFinding, TraceabilityLink


def make_finding(
    finding_id: str,
    title: str,
    description: str,
    severity: str,
    cwe: str,
    recommendation: str = "Fix issue."
):
    return SecurityFinding(
        finding_id=finding_id,
        title=title,
        description=description,
        severity=severity,
        file="sample_ecommerce_app/app.py",
        line=1,
        detection_method="AST",
        cwe=cwe,
        recommendation=recommendation,
        traceability=TraceabilityLink()
    )


def test_fix_suggester_for_hardcoded_secret():
    suggester = SecurityFixSuggester()

    finding = make_finding(
        finding_id="SEC-001",
        title="Hardcoded secret detected",
        description="API_KEY is hardcoded.",
        severity="High",
        cwe="CWE-798"
    )

    fix = suggester.generate_fix_suggestion(finding)

    assert fix.finding_id == "SEC-001"
    assert fix.priority == "High"
    assert fix.effort == "Low"
    assert "environment variables" in fix.recommended_fix
    assert "os.getenv" in fix.example_fix


def test_fix_suggester_for_sql_injection():
    suggester = SecurityFixSuggester()

    finding = make_finding(
        finding_id="SEC-002",
        title="Possible raw SQL string formatting",
        description="SQL query is built using string concatenation.",
        severity="Critical",
        cwe="CWE-89"
    )

    fix = suggester.generate_fix_suggestion(finding)

    assert fix.priority == "Immediate"
    assert fix.effort == "Medium"
    assert "parameterized" in fix.recommended_fix.lower()


def test_fix_suggester_for_eval():
    suggester = SecurityFixSuggester()

    finding = make_finding(
        finding_id="SEC-003",
        title="Use of eval() detected",
        description="eval can execute arbitrary code.",
        severity="Critical",
        cwe="CWE-95"
    )

    fix = suggester.generate_fix_suggestion(finding)

    assert fix.priority == "Immediate"
    assert "eval" in fix.recommended_fix.lower()
    assert "json.loads" in fix.example_fix


def test_fix_suggester_generates_list():
    suggester = SecurityFixSuggester()

    findings = [
        make_finding(
            finding_id="SEC-001",
            title="Hardcoded secret detected",
            description="API key is hardcoded.",
            severity="High",
            cwe="CWE-798"
        ),
        make_finding(
            finding_id="SEC-002",
            title="Use of eval() detected",
            description="eval can execute arbitrary code.",
            severity="Critical",
            cwe="CWE-95"
        )
    ]

    fixes = suggester.generate_fix_suggestions(findings)

    assert len(fixes) == 2
    assert fixes[0].finding_id == "SEC-001"
    assert fixes[1].finding_id == "SEC-002"