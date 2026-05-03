from typing import List, Literal, Optional
from pydantic import BaseModel, Field


class ArchitectureModule(BaseModel):
    """
    Represents one logical architecture module.

    In this MVP we use modular monolith style.
    That means the generated application is one deployable system,
    but internally separated into clear modules such as Catalog, Cart, Order.
    """
    id: str
    name: str
    responsibility: str
    related_requirements: List[str]


class APIEndpoint(BaseModel):
    """
    Internal API contract model.

    The OpenAPI YAML will be generated from this structure.
    Keeping this as JSON first is safer than asking the LLM to directly
    generate YAML.
    """
    id: str
    tag: str
    method: Literal["GET", "POST", "PUT", "PATCH", "DELETE"]
    path: str
    summary: str
    description: str
    request_schema: Optional[str] = None
    response_schema: str
    related_requirements: List[str]


class SDS(BaseModel):
    """
    Software Design Specification.

    This is the main architecture document in machine-readable form.
    It will also be rendered to SDS_v1.md.
    """
    project_name: str
    version: str
    architecture_style: Literal["modular_monolith", "microservices"]
    overview: str
    modules: List[ArchitectureModule]
    api_endpoints: List[APIEndpoint]
    security_considerations: List[str]
    deployment_assumptions: List[str]
    technology_stack: List[str]


class DBAttribute(BaseModel):
    name: str
    type: str
    required: bool = True
    description: str


class DBEntity(BaseModel):
    """
    Represents a database/domain entity.

    This is not migration code yet.
    Later the Coder Agent can convert this into actual models/tables.
    """
    id: str
    name: str
    description: str
    attributes: List[DBAttribute]


class DBRelationship(BaseModel):
    source: str
    target: str
    relationship: str
    description: str


class DBPack(BaseModel):
    """
    Machine-readable database design pack.

    The class diagram will be generated from this DBPack,
    so DBPack becomes the source of truth for data structure.
    """
    project_name: str
    version: str
    database_type: str
    entities: List[DBEntity]
    relationships: List[DBRelationship]
    indexes: List[str]
    constraints: List[str]


class ArchitectureTraceabilityLink(BaseModel):
    """
    Traceability link from requirement to architecture artifact.

    This supports your research novelty:
    FR -> API -> DB -> module -> later UI/code/tests/security.
    """
    requirement_id: str
    artifact_type: Literal["MODULE", "API_ENDPOINT", "DB_ENTITY", "WORKFLOW", "DIAGRAM"]
    artifact_id: str
    description: str


class ArchitectureResult(BaseModel):
    run_id: str
    architecture_version: str
    srs_version: str
    domain_version: str
    sds_path: str
    sds_markdown_path: str
    openapi_path: str
    db_pack_path: str
    db_pack_markdown_path: str
    traceability_path: str
    diagram_paths: List[str]