import json
import math
import logging
import time
from sqlalchemy import text

from app.db.database import engine
from app.rag.embeddings import generate_embedding
from app.rag.loader import load_and_chunk_documents
from app.core.config import settings
logger = logging.getLogger(__name__)
def create_vector_store() -> None:
    with engine.begin() as connection:
        connection.execute(
            text(
                """
                CREATE TABLE IF NOT EXISTS document_embeddings (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    source TEXT NOT NULL,
                    chunk_id INTEGER NOT NULL,
                    content TEXT NOT NULL,
                    embedding TEXT NOT NULL
                )
                """
            )
        )


def store_embedding(
    source: str,
    chunk_id: int,
    content: str,
    embedding: list[float],
) -> None:
    with engine.begin() as connection:
        connection.execute(
            text(
                """
                INSERT INTO document_embeddings
                (source, chunk_id, content, embedding)
                VALUES
                (:source, :chunk_id, :content, :embedding)
                """
            ),
            {
                "source": source,
                "chunk_id": chunk_id,
                "content": content,
                "embedding": json.dumps(embedding),
            },
        )


def cosine_similarity(
    vector_a: list[float],
    vector_b: list[float],
) -> float:
    dot_product = sum(
        a * b
        for a, b in zip(vector_a, vector_b)
    )

    magnitude_a = math.sqrt(
        sum(a * a for a in vector_a)
    )

    magnitude_b = math.sqrt(
        sum(b * b for b in vector_b)
    )

    if magnitude_a == 0 or magnitude_b == 0:
        return 0.0

    return dot_product / (
        magnitude_a * magnitude_b
    )


async def build_knowledge_index() -> int:
    create_vector_store()

    with engine.begin() as connection:
        connection.execute(
            text(
                """
                DELETE FROM document_embeddings
                """
            )
        )

    chunks = load_and_chunk_documents()

    indexed_count = 0

    for chunk in chunks:
        embedding = await generate_embedding(
            chunk["content"]
        )

        store_embedding(
            source=chunk["source"],
            chunk_id=chunk["chunk_id"],
            content=chunk["content"],
            embedding=embedding,
        )

        indexed_count += 1

    return indexed_count

async def retrieve_relevant_chunks(
    query: str,
    top_k: int = 3,
    similarity_threshold: float | None = None,
) -> list[dict]:

    if not query.strip():
        raise ValueError("Query cannot be empty")

    if similarity_threshold is None:
        similarity_threshold = settings.RAG_SIMILARITY_THRESHOLD
    start_time = time.perf_counter()
    query_embedding = await generate_embedding(query)

    with engine.connect() as connection:
        result = connection.execute(
            text(
                """
                SELECT
                    source,
                    chunk_id,
                    content,
                    embedding
                FROM document_embeddings
                """
            )
        )

        rows = result.fetchall()

    scored_chunks = []

    for row in rows:
        stored_embedding = json.loads(
            row.embedding
        )

        similarity = cosine_similarity(
            query_embedding,
            stored_embedding,
        )

        scored_chunks.append(
            {
                "source": row.source,
                "chunk_id": row.chunk_id,
                "content": row.content,
                "similarity": similarity,
            }
        )

    scored_chunks.sort(
        key=lambda item: item["similarity"],
        reverse=True,
    )
    filtered_chunks = [
        chunk
        for chunk in scored_chunks
        if chunk["similarity"] >= similarity_threshold
    ]
    filtered_chunks = [
        chunk
        for chunk in scored_chunks
        if chunk["similarity"] >= similarity_threshold
    ]
    unique_chunks = []
    seen_content = set()

    for chunk in filtered_chunks:
        content = chunk["content"]

        if content in seen_content:
            continue

        seen_content.add(content)
        unique_chunks.append(chunk)

        if len(unique_chunks) == top_k:
            break
    duration_ms = (
        time.perf_counter() - start_time
    ) * 1000

    logger.info(
        "RAG retrieval completed | query_length=%s | "
        "chunks_returned=%s | duration_ms=%.2f",
        len(query),
        len(unique_chunks),
        duration_ms,
    )
    return unique_chunks
    