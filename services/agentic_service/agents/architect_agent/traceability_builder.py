from agents.architect_agent.schemas import (
    ArchitectureTraceabilityLink,
    SDS,
    DBPack,
)


def build_architecture_traceability(
    srs: dict,
    sds: SDS,
    db_pack: DBPack,
) -> list[ArchitectureTraceabilityLink]:
    """
    Builds traceability links from FRs to architecture artifacts.

    This is one of the most important research features:
    it shows how requirements are connected to design decisions.
    """

    links: list[ArchitectureTraceabilityLink] = []

    functional_requirements = srs.get("functional_requirements", [])

    for fr in functional_requirements:
        fr_id = fr.get("id", "")
        fr_text = f"{fr.get('title', '')} {fr.get('description', '')}".lower()

        # Link FR to modules
        for module in sds.modules:
            if fr_id in module.related_requirements:
                links.append(
                    ArchitectureTraceabilityLink(
                        requirement_id=fr_id,
                        artifact_type="MODULE",
                        artifact_id=module.id,
                        description=f"{fr_id} is supported by {module.name}.",
                    )
                )

        # Link FR to API endpoints
        for endpoint in sds.api_endpoints:
            if fr_id in endpoint.related_requirements:
                links.append(
                    ArchitectureTraceabilityLink(
                        requirement_id=fr_id,
                        artifact_type="API_ENDPOINT",
                        artifact_id=f"{endpoint.method} {endpoint.path}",
                        description=f"{fr_id} is implemented through {endpoint.method} {endpoint.path}.",
                    )
                )

        # Link FR to DB entities using keyword matching
        for entity in db_pack.entities:
            entity_name = entity.name.lower()

            if entity_name in fr_text:
                links.append(
                    ArchitectureTraceabilityLink(
                        requirement_id=fr_id,
                        artifact_type="DB_ENTITY",
                        artifact_id=entity.name,
                        description=f"{fr_id} uses the {entity.name} entity.",
                    )
                )

        # Add diagram-level traceability for important flows
        if "checkout" in fr_text:
            links.append(
                ArchitectureTraceabilityLink(
                    requirement_id=fr_id,
                    artifact_type="DIAGRAM",
                    artifact_id="sequence_checkout_v1.mmd",
                    description=f"{fr_id} is represented in the checkout sequence diagram.",
                )
            )

        if "order" in fr_text or "history" in fr_text:
            links.append(
                ArchitectureTraceabilityLink(
                    requirement_id=fr_id,
                    artifact_type="DIAGRAM",
                    artifact_id="sequence_order_history_v1.mmd",
                    description=f"{fr_id} is represented in the order history sequence diagram.",
                )
            )

    return links