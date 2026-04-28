from typing import List, Optional, Literal
from pydantic import BaseModel, Field


class Stakeholder(BaseModel):
    role: str
    description: str


class IntakeInput(BaseModel):
    project_name: str = Field(..., min_length=3)
    business_goal: str = Field(..., min_length=10)
    target_users: List[str] = Field(..., min_length=1)
    stakeholders: List[Stakeholder] = Field(default_factory=list)

    ecommerce_features: List[str] = Field(
        default_factory=lambda: [
            "product browsing",
            "product details",
            "cart operations",
            "checkout",
            "order placement",
            "order history"
        ]
    )

    business_rules: List[str] = Field(default_factory=list)
    constraints: List[str] = Field(default_factory=list)
    assumptions: List[str] = Field(default_factory=list)
    out_of_scope: List[str] = Field(default_factory=list)


class AcceptanceCriteria(BaseModel):
    id: str
    description: str


class FunctionalRequirement(BaseModel):
    id: str
    title: str
    description: str
    priority: Literal["Must", "Should", "Could"]
    acceptance_criteria: List[AcceptanceCriteria]


class NonFunctionalRequirement(BaseModel):
    id: str
    category: str
    description: str
    acceptance_criteria: List[AcceptanceCriteria]


class UseCase(BaseModel):
    id: str
    title: str
    actor: str
    preconditions: List[str]
    main_flow: List[str]
    alternative_flows: List[str]
    related_requirements: List[str]


class SRS(BaseModel):
    project_name: str
    version: str
    domain: Literal["E-commerce"]
    purpose: str
    scope_in: List[str]
    scope_out: List[str]
    roles: List[str]
    stakeholders: List[Stakeholder]
    workflows: List[str]
    business_rules: List[str]
    constraints: List[str]
    assumptions: List[str]
    functional_requirements: List[FunctionalRequirement]
    non_functional_requirements: List[NonFunctionalRequirement]
    use_cases: List[UseCase]