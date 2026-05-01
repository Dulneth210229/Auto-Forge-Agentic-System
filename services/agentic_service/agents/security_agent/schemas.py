from typing import List, Literal
from pydantic import BaseModel, Field


class TraceabilityLink(BaseModel):
    """
    Stores traceability information for a security finding.

    This will later connect:
    Requirement → API → UI → Code → Test → Security Finding → Validation Result
    """

    requirement_id: str = ""
    api: str = ""
    module: str = ""


class SecurityFinding(BaseModel):
    """
    Represents one security issue found by the Security Agent.

    For now, this is filled with dummy data.
    Later, findings will come from:
    - AST static analysis
    - Dependency scanning
    - LLM-assisted secure code review
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

    These are dummy values for now.
    In later steps, these will be calculated using Testing Agent validation.
    """

    coverage: float = 0.0
    confidence: float = 0.0


class SecurityReport(BaseModel):
    """
    Main machine-readable Security Report schema.
    This JSON structure must be saved as SecurityReport_v1.json.
    """

    run_id: str
    stage: Literal["security"] = "security"
    version: str
    summary: SecuritySummary
    findings: List[SecurityFinding]
    dependency_vulnerabilities: List[dict] = []
    llm_findings: List[dict] = []
    metrics: SecurityMetrics