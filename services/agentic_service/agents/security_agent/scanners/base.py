from agents.security_agent.schemas import SecurityFinding, TraceabilityLink


class FindingFactory:
    """
    Helper class for creating SecurityFinding objects with stable SEC IDs.

    All scanners share one FindingFactory so finding IDs remain sequential:
    SEC-001, SEC-002, SEC-003, ...
    """

    def __init__(self):
        self.finding_counter = 1

    def create_finding(
        self,
        title: str,
        description: str,
        severity: str,
        file: str,
        line: int,
        detection_method: str,
        cwe: str,
        recommendation: str,
        requirement_id: str = "",
        api: str = "",
        module: str = ""
    ) -> SecurityFinding:
        finding_id = f"SEC-{self.finding_counter:03d}"
        self.finding_counter += 1

        return SecurityFinding(
            finding_id=finding_id,
            title=title,
            description=description,
            severity=severity,
            file=file,
            line=line,
            detection_method=detection_method,
            cwe=cwe,
            recommendation=recommendation,
            traceability=TraceabilityLink(
                requirement_id=requirement_id,
                api=api,
                module=module
            )
        )