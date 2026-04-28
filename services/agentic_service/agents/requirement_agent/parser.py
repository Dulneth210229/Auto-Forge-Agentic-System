import json
import re
from agents.requirement_agent.schemas import SRS


class SRSParseError(Exception):
    pass


def extract_json(text: str) -> dict:
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    match = re.search(r"\{.*\}", text, re.DOTALL)

    if not match:
        raise SRSParseError("No JSON object found in LLM output.")

    try:
        return json.loads(match.group(0))
    except json.JSONDecodeError as error:
        raise SRSParseError(f"Invalid JSON extracted: {error}")


def parse_srs(text: str) -> SRS:
    data = extract_json(text)
    return SRS.model_validate(data)