from typing import List, Literal
from pydantic import BaseModel, Field


class DomainWorkflowStep(BaseModel):
    """Single step within a domain workflow."""
    step_number: int
    description: str


class DomainWorkflow(BaseModel):
    """Business workflow with steps, exceptions, and related requirements."""
    id: str = Field(..., description="Workflow ID such as WF-001")
    name: str
    actor: str
    description: str
    trigger: str
    steps: List[DomainWorkflowStep]
    exceptions: List[str]
    related_requirements: List[str]


class BusinessRule(BaseModel):
    """Normalized business rule with a category, rationale, and traceability."""
    id: str = Field(..., description="Business rule ID such as BR-001")
    category: Literal[
        "Catalog",
        "Pricing",
        "Stock",
        "Cart",
        "Checkout",
        "Payment",
        "Order",
        "Return",
        "Refund",
        "Discount",
        "General"
    ]
    rule: str
    rationale: str
    related_requirements: List[str]


class DomainException(BaseModel):
    """Exception scenario and expected system response."""
    id: str = Field(..., description="Exception ID such as EX-001")
    scenario: str
    system_response: str
    related_workflow: str


class DomainEntity(BaseModel):
    """Key domain entity and its important fields."""
    id: str = Field(..., description="Entity ID such as DE-001")
    name: str
    description: str
    important_fields: List[str]


class DomainPolicy(BaseModel):
    """Policy statement that governs domain behavior."""
    id: str = Field(..., description="Policy ID such as DP-001")
    name: str
    description: str


class DomainPack(BaseModel):
    """Top-level bundle of extracted domain knowledge for a project."""
    project_name: str
    version: str
    domain: Literal["E-commerce"]
    source_srs_version: str

    domain_summary: str
    retrieved_knowledge_summary: str

    workflows: List[DomainWorkflow]
    business_rules: List[BusinessRule]
    exceptions: List[DomainException]
    domain_entities: List[DomainEntity]
    policies: List[DomainPolicy]

    assumptions: List[str]
    constraints: List[str]
