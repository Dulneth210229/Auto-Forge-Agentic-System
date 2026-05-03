from typing import List


def chunk_text(text: str, chunk_size: int = 900, overlap: int = 150) -> List[str]:
    """
    Splits a large domain knowledge document into smaller chunks.

    Why chunking is needed:
    - LLMs cannot read very large documents at once.
    - Vector databases store and retrieve smaller chunks.
    - Retrieval becomes more accurate when chunks are focused.

    Example:
    Long domain file -> chunk 1, chunk 2, chunk 3...
    """
    if not text.strip():
        return []

    chunks = []
    start = 0
    text_length = len(text)

    while start < text_length:
        end = start + chunk_size
        chunk = text[start:end].strip()

        if chunk:
            chunks.append(chunk)

        # Move forward but keep some overlap so context is not lost.
        start += chunk_size - overlap

    return chunks