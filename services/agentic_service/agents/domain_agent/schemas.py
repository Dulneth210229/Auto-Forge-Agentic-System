from typing import List, Literal, Optional
from pydantic import BaseModel


class RetrievedKnowledgeChunk(BaseModel):
    """
    Stores one chunk retrieved from the vector database.

    This is important for RAG traceability because later we can show
    which domain knowledge chunks influenced the generated DomainPack.
    """
    chunk_id: str
    source: str
    content: str
    score: Optional[float] = None


class DomainWorkflow(BaseModel):
    """
    Represents one E-commerce workflow.
    Example: Product browsing, cart update, checkout, order placement.
    """
    id: str
    name: str
    description: str
    actors: List[str]
    steps: List[str]
    exceptions: List[str]
    related_requirements: List[str]


class DomainBusinessRule(BaseModel):
    """
    Represents an E-commerce business rule.
    Example: Customers cannot checkout with out-of-stock items.
    """
    id: str
    title: str
    description: str
    related_requirements: List[str]


class DomainEntity(BaseModel):
    """
    Represents an important domain concept.

    This is not yet a database table. The Architect Agent will later use
    these entities to design tables/entities/API resources.
    """
    id: str
    name: str
    description: str
    key_attributes: List[str]


class DomainException(BaseModel):
    """
    Represents business exceptions that can happen in E-commerce flows.
    Example: payment failure, invalid coupon, out-of-stock item.
    """
    id: str
    name: str
    description: str
    handling_rule: str


class DomainPack(BaseModel):
    """
    Final output schema of the Domain Agent.
    This is saved as DomainPack_v1.json and rendered to DomainPack_v1.md.
    """
    project_name: str
    version: str
    domain: Literal["E-commerce"]

    overview: str

    workflows: List[DomainWorkflow]
    business_rules: List[DomainBusinessRule]
    domain_entities: List[DomainEntity]
    exceptions: List[DomainException]

    assumptions: List[str]
    constraints: List[str]

    retrieved_knowledge: List[RetrievedKnowledgeChunk]