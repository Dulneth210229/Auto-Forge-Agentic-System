import json
import os
from pathlib import Path

from agents.domain_agent.chunker import chunk_text
from agents.domain_agent.vector_store import DomainVectorStore, VectorStoreType
from agents.domain_agent.retriever import DomainRetriever
from agents.domain_agent.prompt import build_domain_pack_prompt
from agents.domain_agent.parser import parse_domain_pack
from agents.domain_agent.renderer import render_domain_pack_markdown

from tools.llm.provider import LLMProvider


class DomainAgent:
    """
    RAG-based Domain Agent.

    Responsibilities:
    1. Ingest E-commerce domain knowledge from a text file.
    2. Store chunks in FAISS or ChromaDB.
    3. Retrieve relevant knowledge using the approved SRS.
    4. Generate DomainPack JSON using LLM.
    5. Validate the output using Pydantic.
    6. Save JSON and Markdown outputs with versioning.
    """

    def __init__(self, llm_provider: LLMProvider):
        self.llm_provider = llm_provider
        self.output_dir = Path(os.getenv("OUTPUT_DIR", "outputs"))

    def ingest_domain_knowledge(
        self,
        file_path: str,
        vector_store_type: VectorStoreType = "faiss"
    ) -> dict:
        """
        Reads the E-commerce domain knowledge file and stores it in vector DB.
        """
        path = Path(file_path)

        if not path.exists():
            raise FileNotFoundError(f"Domain knowledge file not found: {file_path}")

        text = path.read_text(encoding="utf-8")

        chunks = chunk_text(
            text=text,
            chunk_size=900,
            overlap=150
        )

        if not chunks:
            raise ValueError("No text chunks created from domain knowledge file.")

        vector_store = DomainVectorStore(store_type=vector_store_type)

        result = vector_store.ingest(
            chunks=chunks,
            source_name=path.name
        )

        return result

    async def generate_domain_pack(
        self,
        run_id: str,
        srs_version: str = "v1",
        domain_version: str = "v1",
        vector_store_type: VectorStoreType = "faiss",
        top_k: int = 6
    ) -> dict:
        """
        Generates DomainPack using approved SRS + retrieved domain knowledge.
        """
        srs_path = (
            self.output_dir
            / "runs"
            / run_id
            / "srs"
            / srs_version
            / f"SRS_{srs_version}.json"
        )

        if not srs_path.exists():
            raise FileNotFoundError(f"SRS file not found: {srs_path}")

        srs = json.loads(srs_path.read_text(encoding="utf-8"))

        retriever = DomainRetriever(vector_store_type=vector_store_type)

        retrieved_chunks = retriever.retrieve_for_srs(
            srs=srs,
            top_k=top_k
        )

        if not retrieved_chunks:
            raise ValueError(
                "No domain knowledge retrieved. Please ingest domain knowledge first."
            )

        prompt = build_domain_pack_prompt(
            srs=srs,
            retrieved_chunks=retrieved_chunks,
            version=domain_version
        )

        llm_output = await self.llm_provider.generate(prompt)

        domain_pack = parse_domain_pack(
            text=llm_output,
            retrieved_chunks=retrieved_chunks
        )

        domain_pack.version = domain_version

        markdown = render_domain_pack_markdown(domain_pack)

        output_path = (
            self.output_dir
            / "runs"
            / run_id
            / "domain"
            / domain_version
        )

        output_path.mkdir(parents=True, exist_ok=True)

        json_file = output_path / f"DomainPack_{domain_version}.json"
        md_file = output_path / f"DomainPack_{domain_version}.md"

        json_file.write_text(
            json.dumps(domain_pack.model_dump(), indent=2),
            encoding="utf-8"
        )

        md_file.write_text(markdown, encoding="utf-8")

        return {
            "run_id": run_id,
            "srs_version": srs_version,
            "domain_version": domain_version,
            "vector_store_type": vector_store_type,
            "json_path": str(json_file),
            "markdown_path": str(md_file),
            "retrieved_chunks_count": len(retrieved_chunks),
            "domain_pack": domain_pack.model_dump()
        }