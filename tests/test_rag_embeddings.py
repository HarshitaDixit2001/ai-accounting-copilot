import pytest

from app.rag.embeddings import generate_embedding


@pytest.mark.asyncio
async def test_generate_embedding():
    embedding = await generate_embedding(
        "What is a journal entry?"
    )

    assert embedding
    assert isinstance(embedding, list)
    assert len(embedding) > 0

    assert all(
        isinstance(value, float)
        for value in embedding
    )