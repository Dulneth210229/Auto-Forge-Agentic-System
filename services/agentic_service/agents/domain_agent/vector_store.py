from pathlib import Path
from typing import List, Literal
import json
import numpy as np

from sentence_transformers import SentenceTransformer

import faiss
import chromadb


VectorStoreType = Literal["faiss", "chroma"]


class EmbeddingModel:
    """
    Wrapper around SentenceTransformer.

    We use one local embedding model to convert text chunks into vectors.
    These vectors are then stored in FAISS or ChromaDB.

    First run may take time because the embedding model can be downloaded.
    """
    def __init__(self, model_name: str = "sentence-transformers/all-MiniLM-L6-v2"):
        self.model = SentenceTransformer(model_name)

    def embed_texts(self, texts: List[str]) -> np.ndarray:
        embeddings = self.model.encode(
            texts,
            convert_to_numpy=True,
            normalize_embeddings=True
        )
        return embeddings.astype("float32")

    def embed_query(self, query: str) -> np.ndarray:
        embedding = self.model.encode(
            [query],
            convert_to_numpy=True,
            normalize_embeddings=True
        )
        return embedding.astype("float32")


class DomainVectorStore:
    """
    Handles storing and retrieving domain knowledge chunks.

    This class supports two vector store engines:
    1. FAISS
    2. ChromaDB

    FAISS is fast and local.
    ChromaDB is easier to inspect and extend later.
    """
    def __init__(
        self,
        store_type: VectorStoreType,
        persist_dir: str = "outputs/vectorstores/domain",
    ):
        self.store_type = store_type
        self.persist_dir = Path(persist_dir)
        self.persist_dir.mkdir(parents=True, exist_ok=True)

        self.embedding_model = EmbeddingModel()

    def ingest(self, chunks: List[str], source_name: str) -> dict:
        """
        Ingest chunks into selected vector store.
        """
        if self.store_type == "faiss":
            return self._ingest_faiss(chunks, source_name)

        if self.store_type == "chroma":
            return self._ingest_chroma(chunks, source_name)

        raise ValueError(f"Unsupported vector store type: {self.store_type}")

    def search(self, query: str, top_k: int = 5) -> List[dict]:
        """
        Search relevant chunks from selected vector store.
        """
        if self.store_type == "faiss":
            return self._search_faiss(query, top_k)

        if self.store_type == "chroma":
            return self._search_chroma(query, top_k)

        raise ValueError(f"Unsupported vector store type: {self.store_type}")

    # -----------------------------
    # FAISS implementation
    # -----------------------------

    def _ingest_faiss(self, chunks: List[str], source_name: str) -> dict:
        embeddings = self.embedding_model.embed_texts(chunks)

        dimension = embeddings.shape[1]

        # IndexFlatIP uses inner product similarity.
        # Because embeddings are normalized, this works like cosine similarity.
        index = faiss.IndexFlatIP(dimension)
        index.add(embeddings)

        faiss_dir = self.persist_dir / "faiss"
        faiss_dir.mkdir(parents=True, exist_ok=True)

        faiss.write_index(index, str(faiss_dir / "domain.index"))

        metadata = []
        for i, chunk in enumerate(chunks):
            metadata.append(
                {
                    "chunk_id": f"CHUNK-{i + 1:04d}",
                    "source": source_name,
                    "content": chunk,
                }
            )

        (faiss_dir / "metadata.json").write_text(
            json.dumps(metadata, indent=2),
            encoding="utf-8"
        )

        return {
            "store_type": "faiss",
            "chunks_ingested": len(chunks),
            "index_path": str(faiss_dir / "domain.index"),
            "metadata_path": str(faiss_dir / "metadata.json"),
        }

    def _search_faiss(self, query: str, top_k: int) -> List[dict]:
        faiss_dir = self.persist_dir / "faiss"
        index_path = faiss_dir / "domain.index"
        metadata_path = faiss_dir / "metadata.json"

        if not index_path.exists() or not metadata_path.exists():
            raise FileNotFoundError(
                "FAISS index not found. Please ingest domain knowledge first."
            )

        index = faiss.read_index(str(index_path))
        metadata = json.loads(metadata_path.read_text(encoding="utf-8"))

        query_embedding = self.embedding_model.embed_query(query)

        scores, indices = index.search(query_embedding, top_k)

        results = []

        for score, idx in zip(scores[0], indices[0]):
            if idx == -1:
                continue

            item = metadata[idx]
            item["score"] = float(score)
            results.append(item)

        return results

    # -----------------------------
    # ChromaDB implementation
    # -----------------------------

    def _ingest_chroma(self, chunks: List[str], source_name: str) -> dict:
        chroma_dir = self.persist_dir / "chroma"

        client = chromadb.PersistentClient(path=str(chroma_dir))

        collection = client.get_or_create_collection(
            name="ecommerce_domain_knowledge"
        )

        ids = []
        metadatas = []
        embeddings = self.embedding_model.embed_texts(chunks)

        for i, chunk in enumerate(chunks):
            ids.append(f"CHUNK-{i + 1:04d}")
            metadatas.append(
                {
                    "source": source_name,
                    "chunk_id": f"CHUNK-{i + 1:04d}",
                }
            )

        # Clear old collection data by deleting existing IDs if needed.
        # For MVP simplicity, we add/update same IDs.
        collection.upsert(
            ids=ids,
            documents=chunks,
            metadatas=metadatas,
            embeddings=embeddings.tolist()
        )

        return {
            "store_type": "chroma",
            "chunks_ingested": len(chunks),
            "collection": "ecommerce_domain_knowledge",
            "persist_dir": str(chroma_dir),
        }

    def _search_chroma(self, query: str, top_k: int) -> List[dict]:
        chroma_dir = self.persist_dir / "chroma"

        client = chromadb.PersistentClient(path=str(chroma_dir))

        collection = client.get_or_create_collection(
            name="ecommerce_domain_knowledge"
        )

        query_embedding = self.embedding_model.embed_query(query)

        response = collection.query(
            query_embeddings=query_embedding.tolist(),
            n_results=top_k
        )

        results = []

        documents = response.get("documents", [[]])[0]
        metadatas = response.get("metadatas", [[]])[0]
        distances = response.get("distances", [[]])[0]

        for document, metadata, distance in zip(documents, metadatas, distances):
            results.append(
                {
                    "chunk_id": metadata.get("chunk_id", ""),
                    "source": metadata.get("source", ""),
                    "content": document,
                    "score": float(distance),
                }
            )

        return results