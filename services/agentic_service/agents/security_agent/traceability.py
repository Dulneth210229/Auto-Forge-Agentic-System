from typing import List

from agents.security_agent.schemas import SecurityFinding, TraceabilityLink


class SecurityTraceabilityMapper:
    """
    Maps security findings to requirement IDs, API endpoints, and system modules.

    This is an MVP rule-based mapper.

    Later, when Architect Agent and Coder Agent are implemented, this mapper can use:
    - SRS_v1.json
    - APIContract_v1.json
    - generated code metadata
    - route registry
    - artifact registry

    For now, it maps based on:
    - file path
    - finding title
    - finding description
    - recommendation text
    """

    MODULE_RULES = [
        {
            "module": "catalog",
            "requirement_id": "FR-001",
            "api": "/products",
            "keywords": [
                "product",
                "products",
                "catalog",
                "search",
                "search_product"
            ]
        },
        {
            "module": "cart",
            "requirement_id": "FR-002",
            "api": "/cart",
            "keywords": [
                "cart",
                "basket"
            ]
        },
        {
            "module": "checkout",
            "requirement_id": "FR-003",
            "api": "/checkout",
            "keywords": [
                "checkout",
                "payment",
                "pay",
                "total",
                "billing"
            ]
        },
        {
            "module": "order",
            "requirement_id": "FR-004",
            "api": "/orders",
            "keywords": [
                "order",
                "orders",
                "purchase",
                "place order"
            ]
        },
        {
            "module": "authentication",
            "requirement_id": "FR-005",
            "api": "/auth",
            "keywords": [
                "auth",
                "login",
                "logout",
                "jwt",
                "token",
                "session",
                "credential"
            ]
        },
        {
            "module": "admin",
            "requirement_id": "FR-006",
            "api": "/admin",
            "keywords": [
                "admin",
                "dashboard",
                "manage"
            ]
        },
        {
            "module": "security_configuration",
            "requirement_id": "NFR-001",
            "api": "N/A",
            "keywords": [
                "cors",
                "debug",
                "docker",
                "environment",
                ".env",
                "secret",
                "api key",
                "password",
                "container",
                "root"
            ]
        },
        {
            "module": "dependency_management",
            "requirement_id": "NFR-002",
            "api": "N/A",
            "keywords": [
                "dependency",
                "package",
                "requirements.txt",
                "package.json",
                "vulnerable dependency",
                "osv",
                "lodash",
                "axios",
                "django",
                "flask",
                "requests",
                "express"
            ]
        },
        {
            "module": "frontend",
            "requirement_id": "FR-007",
            "api": "UI",
            "keywords": [
                "frontend",
                "innerhtml",
                "localstorage",
                "local storage",
                "react",
                "javascript",
                "xss"
            ]
        }
    ]

    DEFAULT_TRACEABILITY = TraceabilityLink(
        requirement_id="NFR-SEC-001",
        api="N/A",
        module="general_security"
    )

    def map_findings(self, findings: List[SecurityFinding]) -> List[SecurityFinding]:
        """
        Add traceability data to every security finding.
        """

        for finding in findings:
            finding.traceability = self.map_finding(finding)

        return findings

    def map_finding(self, finding: SecurityFinding) -> TraceabilityLink:
        """
        Map a single finding to a TraceabilityLink.
        """

        text = self._build_search_text(finding)

        for rule in self.MODULE_RULES:
            if self._matches_rule(text, rule["keywords"]):
                return TraceabilityLink(
                    requirement_id=rule["requirement_id"],
                    api=rule["api"],
                    module=rule["module"]
                )

        return self.DEFAULT_TRACEABILITY

    def _build_search_text(self, finding: SecurityFinding) -> str:
        """
        Build normalized searchable text from the finding.
        """

        return (
            f"{finding.title} "
            f"{finding.description} "
            f"{finding.recommendation} "
            f"{finding.file} "
            f"{finding.cwe}"
        ).lower().replace("\\", "/")

    def _matches_rule(self, text: str, keywords: List[str]) -> bool:
        """
        Check whether any rule keyword appears in the finding text.
        """

        for keyword in keywords:
            if keyword.lower() in text:
                return True

        return False