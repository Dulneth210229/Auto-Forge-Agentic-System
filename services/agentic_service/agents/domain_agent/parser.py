import json
import re
from agents.domain_agent.schemas import DomainPack, RetrievedKnowledgeChunk


class DomainPackParseError(Exception):
    pass


def extract_json(text: str) -> dict:
    """
    Safely extracts JSON from LLM output.

    Sometimes an LLM may return:
    'Here is the JSON: {...}'

    This function tries to extract only the JSON object.
    """
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    match = re.search(r"\{.*\}", text, re.DOTALL)

    if not match:
        raise DomainPackParseError("No JSON object found in Domain Agent output.")

    try:
        return json.loads(match.group(0))
    except json.JSONDecodeError as error:
        raise DomainPackParseError(f"Invalid JSON extracted: {error}")


def parse_domain_pack(text: str, retrieved_chunks: list[dict]) -> DomainPack:
    """
    Converts raw LLM text into validated DomainPack.

    We inject retrieved_knowledge ourselves to make traceability more reliable.
    """
    data = extract_json(text)

    data["retrieved_knowledge"] = [
        RetrievedKnowledgeChunk.model_validate(chunk).model_dump()
        for chunk in retrieved_chunks
    ]

    return DomainPack.model_validate(data)