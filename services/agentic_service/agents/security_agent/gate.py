from typing import List

from agents.security_agent.schemas import SecurityFinding, SecurityGateDecision


class SecurityGateEvaluator:
    """
    Evaluates whether generated code can pass the security gate.

    Gate policy:
    - FAIL if one or more Critical findings exist
    - FAIL if High findings exceed the allowed threshold
    - WARN if Medium findings exist but no blocking findings exist
    - PASS if no Critical/High/Medium findings exist
    """

    MAX_ALLOWED_HIGH_FINDINGS = 2

    def evaluate(self, findings: List[SecurityFinding]) -> SecurityGateDecision:
        critical_findings = [
            finding for finding in findings
            if finding.severity == "Critical"
        ]

        high_findings = [
            finding for finding in findings
            if finding.severity == "High"
        ]

        medium_findings = [
            finding for finding in findings
            if finding.severity == "Medium"
        ]

        if critical_findings:
            return SecurityGateDecision(
                status="FAIL",
                reason="Security gate failed because Critical vulnerabilities were detected.",
                policy="FAIL if one or more Critical findings exist.",
                blocking_findings=[finding.finding_id for finding in critical_findings]
            )

        if len(high_findings) > self.MAX_ALLOWED_HIGH_FINDINGS:
            return SecurityGateDecision(
                status="FAIL",
                reason=(
                    f"Security gate failed because High severity findings exceeded "
                    f"the allowed threshold of {self.MAX_ALLOWED_HIGH_FINDINGS}."
                ),
                policy=f"FAIL if High findings are greater than {self.MAX_ALLOWED_HIGH_FINDINGS}.",
                blocking_findings=[finding.finding_id for finding in high_findings]
            )

        if high_findings:
            return SecurityGateDecision(
                status="WARN",
                reason="Security gate warning because High severity findings exist but are within threshold.",
                policy=f"WARN if High findings are present but not greater than {self.MAX_ALLOWED_HIGH_FINDINGS}.",
                blocking_findings=[finding.finding_id for finding in high_findings]
            )

        if medium_findings:
            return SecurityGateDecision(
                status="WARN",
                reason="Security gate warning because Medium severity findings were detected.",
                policy="WARN if Medium findings exist and no Critical or blocking High findings exist.",
                blocking_findings=[]
            )

        return SecurityGateDecision(
            status="PASS",
            reason="Security gate passed because no blocking findings were detected.",
            policy="PASS if no Critical, High, or Medium findings exist.",
            blocking_findings=[]
        )