from agents.security_agent.traceability import SecurityTraceabilityMapper
from agents.security_agent.schemas import SecurityFinding, TraceabilityLink


def make_finding(
    title: str,
    description: str,
    file: str,
    cwe: str = "N/A",
    recommendation: str = "Fix issue."
):
    return SecurityFinding(
        finding_id="SEC-001",
        title=title,
        description=description,
        severity="High",
        file=file,
        line=1,
        detection_method="AST",
        cwe=cwe,
        recommendation=recommendation,
        traceability=TraceabilityLink()
    )


def test_traceability_maps_catalog_finding():
    mapper = SecurityTraceabilityMapper()

    finding = make_finding(
        title="Possible raw SQL string formatting",
        description="The search_product endpoint builds a SQL query using product search input.",
        file="sample_ecommerce_app/app.py",
        cwe="CWE-89",
        recommendation="Use parameterized queries for product search."
    )

    traceability = mapper.map_finding(finding)

    assert traceability.requirement_id == "FR-001"
    assert traceability.api == "/products"
    assert traceability.module == "catalog"


def test_traceability_maps_checkout_finding():
    mapper = SecurityTraceabilityMapper()

    finding = make_finding(
        title="Payment validation issue",
        description="Checkout payment input is not validated.",
        file="sample_ecommerce_app/checkout.py",
        cwe="CWE-20",
        recommendation="Validate payment and checkout data."
    )

    traceability = mapper.map_finding(finding)

    assert traceability.requirement_id == "FR-003"
    assert traceability.api == "/checkout"
    assert traceability.module == "checkout"


def test_traceability_maps_dependency_finding():
    mapper = SecurityTraceabilityMapper()

    finding = make_finding(
        title="Vulnerable dependency detected: lodash",
        description="Package lodash has a known vulnerability.",
        file="sample_ecommerce_app/package.json",
        cwe="CWE-937",
        recommendation="Upgrade the vulnerable dependency."
    )

    traceability = mapper.map_finding(finding)

    assert traceability.requirement_id == "NFR-002"
    assert traceability.api == "N/A"
    assert traceability.module == "dependency_management"


def test_traceability_maps_frontend_finding():
    mapper = SecurityTraceabilityMapper()

    finding = make_finding(
        title="Direct innerHTML assignment detected",
        description="innerHTML may introduce XSS in frontend JavaScript.",
        file="sample_ecommerce_app/frontend.js",
        cwe="CWE-79",
        recommendation="Use textContent or sanitize HTML."
    )

    traceability = mapper.map_finding(finding)

    assert traceability.requirement_id == "FR-007"
    assert traceability.api == "UI"
    assert traceability.module == "frontend"


def test_traceability_default_mapping():
    mapper = SecurityTraceabilityMapper()

    finding = make_finding(
        title="Unknown security issue",
        description="This issue does not match any known module keyword.",
        file="sample_ecommerce_app/unknown.py",
        cwe="CWE-000",
        recommendation="Review manually."
    )

    traceability = mapper.map_finding(finding)

    assert traceability.requirement_id == "NFR-SEC-001"
    assert traceability.api == "N/A"
    assert traceability.module == "general_security"


def test_traceability_maps_list_of_findings():
    mapper = SecurityTraceabilityMapper()

    findings = [
        make_finding(
            title="Vulnerable dependency detected: axios",
            description="Package axios has a vulnerability.",
            file="sample_ecommerce_app/package.json",
            cwe="CWE-937"
        ),
        make_finding(
            title="Sensitive token stored in localStorage",
            description="Token is stored in browser local storage.",
            file="sample_ecommerce_app/frontend.js",
            cwe="CWE-922"
        )
    ]

    mapped_findings = mapper.map_findings(findings)

    assert mapped_findings[0].traceability.module == "dependency_management"
    assert mapped_findings[1].traceability.module == "authentication"