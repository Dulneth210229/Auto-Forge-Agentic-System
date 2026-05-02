from agents.domain_agent.vector_store import DomainVectorStore, VectorStoreType


class DomainRetriever:
    """
    Retrieves E-commerce domain knowledge related to the SRS.

    The Domain Agent does not blindly generate.
    It first retrieves relevant domain knowledge chunks from the vector store.
    """
    def __init__(self, vector_store_type: VectorStoreType):
        self.vector_store = DomainVectorStore(store_type=vector_store_type)

    def retrieve_for_srs(self, srs: dict, top_k: int = 6) -> list[dict]:
        """
        Builds a search query from the SRS and retrieves relevant knowledge.
        """
        project_name = srs.get("project_name", "")
        purpose = srs.get("purpose", "")

        fr_text = " ".join(
            [
                f"{fr.get('id', '')} {fr.get('title', '')} {fr.get('description', '')}"
                for fr in srs.get("functional_requirements", [])
            ]
        )

        query = f"""
        E-commerce domain workflows and business rules for:
        Project: {project_name}
        Purpose: {purpose}
        Functional requirements: {fr_text}
        """

        return self.vector_store.search(query=query, top_k=top_k)