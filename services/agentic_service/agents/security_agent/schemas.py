from typing import List, Literal
from pydantic import BaseModel, Field


class TraceabilityLink(BaseModel):
    """
    Stores traceability information for a security finding.
    """

    requirement_id: str = ""
    api: str = ""
    module: str = ""


class SecurityFinding(BaseModel):
    """
    Represents one security issue found by the Security Agent.
    """

    finding_id: str
    title: str
    description: str
    severity: Literal["Critical", "High", "Medium", "Low"]
    file: str
    line: int = Field(ge=0)
    detection_method: Literal["AST", "Dependency", "LLM"]
    cwe: str
    recommendation: str
    traceability: TraceabilityLink


class SecuritySummary(BaseModel):
    """
    Summary counts for all detected security findings.
    """

    total_findings: int = 0
    critical: int = 0
    high: int = 0
    medium: int = 0
    low: int = 0


class SecurityMetrics(BaseModel):
    """
    Basic evaluation metrics.
    """

    coverage: float = 0.0
    confidence: float = 0.0


class SecurityGateDecision(BaseModel):
    """
    Final security gate decision.
    """

    status: Literal["PASS", "WARN", "FAIL"]
    reason: str
    policy: str
    blocking_findings: List[str] = []


class SecurityFixSuggestion(BaseModel):
    """
    Structured remediation guidance for one security finding.

    This helps the Coder Agent or developer understand how to fix the issue.
    """

    finding_id: str
    issue: str
    severity: Literal["Critical", "High", "Medium", "Low"]
    file: str
    recommended_fix: str
    example_fix: str
    priority: Literal["Immediate", "High", "Normal", "Low"]
    effort: Literal["Low", "Medium", "High"]


class SecurityReport(BaseModel):
    """
    Main machine-readable Security Report schema.
    This JSON structure is saved as SecurityReport_v1.json.
    """

    run_id: str
    stage: Literal["security"] = "security"
    version: str
    summary: SecuritySummary
    findings: List[SecurityFinding]
    dependency_vulnerabilities: List[dict] = []
    llm_findings: List[dict] = []
    security_gate: SecurityGateDecision
    fix_suggestions: List[SecurityFixSuggestion] = []
    metrics: SecurityMetrics