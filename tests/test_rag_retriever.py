import pytest
from unittest.mock import AsyncMock, patch

from app.rag.retriever import (
    cosine_similarity,
    build_knowledge_index,
    retrieve_relevant_chunks,
)


def test_cosine_similarity_identical_vectors():
    vector = [1.0, 2.0, 3.0]

    similarity = cosine_similarity(
        vector,
        vector,
    )

    assert similarity == 1.0


def test_cosine_similarity_different_vectors():
    vector_a = [1.0, 0.0]
    vector_b = [0.0, 1.0]

    similarity = cosine_similarity(
        vector_a,
        vector_b,
    )

    assert similarity == 0.0


def test_cosine_similarity_zero_vector():
    vector_a = [0.0, 0.0]
    vector_b = [1.0, 2.0]

    similarity = cosine_similarity(
        vector_a,
        vector_b,
    )

    assert similarity == 0.0


@pytest.mark.asyncio
async def test_build_knowledge_index():
    indexed_count = await build_knowledge_index()

    assert indexed_count > 0


@pytest.mark.asyncio
async def test_retrieve_relevant_chunks():
    results = await retrieve_relevant_chunks(
        "How do I record rent paid in cash?",
        top_k=3,
    )

    assert results
    assert len(results) <= 3

    for result in results:
        assert result["source"]
        assert result["content"]
        assert "similarity" in result


@pytest.mark.asyncio
async def test_retrieve_respects_similarity_threshold():
    fake_embedding = [1.0, 0.0]

    fake_rows = [
        {
            "source": "accounting_basics.txt",
            "chunk_id": 0,
            "content": "Relevant accounting information.",
            "embedding": [1.0, 0.0],
        },
        {
            "source": "journal_entries.txt",
            "chunk_id": 1,
            "content": "Less relevant accounting information.",
            "embedding": [0.0, 1.0],
        },
    ]

    class FakeConnection:
        def __enter__(self):
            return self

        def __exit__(
            self,
            exc_type,
            exc_value,
            traceback,
        ):
            return False

        def execute(self, *args, **kwargs):
            class FakeResult:
                def fetchall(self):
                    class Row:
                        def __init__(
                            self,
                            source,
                            chunk_id,
                            content,
                            embedding,
                        ):
                            self.source = source
                            self.chunk_id = chunk_id
                            self.content = content
                            self.embedding = embedding

                    import json

                    return [
                        Row(
                            row["source"],
                            row["chunk_id"],
                            row["content"],
                            json.dumps(row["embedding"]),
                        )
                        for row in fake_rows
                    ]

            return FakeResult()

    class FakeEngine:
        def connect(self):
            return FakeConnection()

    with patch(
        "app.rag.retriever.generate_embedding",
        new_callable=AsyncMock,
        return_value=fake_embedding,
    ), patch(
        "app.rag.retriever.engine",
        FakeEngine(),
    ):
        results = await retrieve_relevant_chunks(
            "accounting question",
            top_k=3,
            similarity_threshold=0.45,
        )

    assert len(results) == 1
    assert results[0]["source"] == "accounting_basics.txt"
    assert results[0]["similarity"] >= 0.45

@pytest.mark.asyncio
async def test_retrieve_uses_configured_similarity_threshold():
    fake_embedding = [1.0, 0.0]

    fake_rows = [
        {
            "source": "accounting_basics.txt",
            "chunk_id": 0,
            "content": "Relevant accounting information.",
            "embedding": [1.0, 0.0],
        },
        {
            "source": "journal_entries.txt",
            "chunk_id": 1,
            "content": "Low similarity information.",
            "embedding": [0.0, 1.0],
        },
    ]

    class FakeConnection:
        def __enter__(self):
            return self

        def __exit__(
            self,
            exc_type,
            exc_value,
            traceback,
        ):
            return False

        def execute(self, *args, **kwargs):
            class FakeResult:
                def fetchall(self):
                    class Row:
                        def __init__(
                            self,
                            source,
                            chunk_id,
                            content,
                            embedding,
                        ):
                            self.source = source
                            self.chunk_id = chunk_id
                            self.content = content
                            self.embedding = embedding

                    import json

                    return [
                        Row(
                            row["source"],
                            row["chunk_id"],
                            row["content"],
                            json.dumps(row["embedding"]),
                        )
                        for row in fake_rows
                    ]

            return FakeResult()

    class FakeEngine:
        def connect(self):
            return FakeConnection()

    with patch(
        "app.rag.retriever.generate_embedding",
        new_callable=AsyncMock,
        return_value=fake_embedding,
    ), patch(
        "app.rag.retriever.engine",
        FakeEngine(),
    ), patch(
        "app.rag.retriever.settings.RAG_SIMILARITY_THRESHOLD",
        0.95,
    ):

        results = await retrieve_relevant_chunks(
            "accounting question",
            top_k=3,
        )

    assert len(results) == 1
    assert results[0]["source"] == "accounting_basics.txt"
    assert results[0]["similarity"] >= 0.95

