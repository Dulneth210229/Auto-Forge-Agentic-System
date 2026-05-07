from pydantic import BaseModel
from typing import List


class CodeGenRequest(BaseModel):
    run_id: str
    srs_version: str = "v1"
    domain_version: str = "v1"
    architecture_version: str = "v1"
    code_version: str = "v1"


class GeneratedFile(BaseModel):
    path: str
    purpose: str
    owner_agent: str


class ResponsibilitySummary(BaseModel):
    agent_name: str
    responsibility: str
    outputs: List[str]


class TraceabilityLink(BaseModel):
    requirement_id: str
    requirement_title: str
    generated_files: List[str]
    api_endpoints: List[str]


class InputArtifactSummary(BaseModel):
    artifact_name: str
    version: str
    path: str


class CodeManifest(BaseModel):
    run_id: str
    code_version: str
    source_srs_version: str
    output_dir: str

    input_artifacts: List[InputArtifactSummary]

    generated_files: List[GeneratedFile]
    responsibilities: List[ResponsibilitySummary]
    traceability_links: List[TraceabilityLink]
    run_instructions: List[str]

    validation_warnings: List[str] = []