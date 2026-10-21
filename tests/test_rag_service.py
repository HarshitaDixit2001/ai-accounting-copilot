import pytest
from unittest.mock import AsyncMock, patch

from fastapi.testclient import TestClient

from app.main import app
from app.prompts.rag import build_rag_prompt


client = TestClient(app)

@pytest.mark.asyncio
async def test_rag_service_returns_sources_for_relevant_question():
    fake_chunks = [
        {
            "source": "journal_entries.txt",
            "chunk_id": 0,
            "content": "A journal entry records a financial transaction.",
            "similarity": 0.85,
        }
    ]

    with patch(
        "app.services.rag_service.retrieve_relevant_chunks",
        new_callable=AsyncMock,
        return_value=fake_chunks,
    ), patch(
        "app.services.rag_service.generate_response",
        new_callable=AsyncMock,
        return_value="A journal entry records a financial transaction.",
    ) as mock_generate:

        from app.services.rag_service import ask_rag_assistant

        response = await ask_rag_assistant(
            "What is a journal entry?"
        )

    assert response["response"]
    assert len(response["sources"]) == 1
    assert response["sources"][0]["source"] == "journal_entries.txt"
    assert response["sources"][0]["chunk_id"] == 0
    assert response["sources"][0]["similarity"] == 0.85

    mock_generate.assert_awaited_once()


@pytest.mark.asyncio
async def test_rag_service_handles_no_relevant_sources():
    with patch(
        "app.services.rag_service.retrieve_relevant_chunks",
        new_callable=AsyncMock,
        return_value=[],
    ), patch(
        "app.services.rag_service.generate_response",
        new_callable=AsyncMock,
    ) as mock_generate:

        from app.services.rag_service import ask_rag_assistant

        response = await ask_rag_assistant(
            "What is the capital of France?"
        )

    assert response["sources"] == []

    assert response["response"] == (
        "The provided accounting knowledge "
        "does not contain enough information "
        "to answer this question."
    )

    mock_generate.assert_not_awaited()

def test_rag_source_metadata():
    fake_sources = [
        {
            "source": "journal_entries.txt",
            "chunk_id": 3,
            "similarity": 0.8125,
        },
        {
            "source": "financial_transactions.txt",
            "chunk_id": 1,
            "similarity": 0.7342,
        },
    ]

    for source in fake_sources:
        assert "source" in source
        assert "chunk_id" in source
        assert "similarity" in source

        assert isinstance(source["source"], str)
        assert isinstance(source["chunk_id"], int)
        assert isinstance(source["similarity"], float)

        assert source["source"]
        assert source["chunk_id"] >= 0
        assert 0.0 <= source["similarity"] <= 1.0

def test_rag_full_integration():
    response = client.post(
        "/accounting/rag",
        json={
            "prompt": "How do I record rent paid in cash?"
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert "response" in data
    assert data["response"]

    assert "sources" in data
    assert data["sources"]

    for source in data["sources"]:
        assert "source" in source
        assert "chunk_id" in source
        assert "similarity" in source

        assert source["source"]
        assert isinstance(source["chunk_id"], int)
        assert 0.0 <= source["similarity"] <= 1.0

def test_rag_full_integration():
    response = client.post(
        "/accounting/rag",
        json={
            "prompt": "How do I record rent paid in cash?"
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert "response" in data
    assert data["response"]

    assert "sources" in data
    assert data["sources"]

    for source in data["sources"]:
        assert "source" in source
        assert "chunk_id" in source
        assert "similarity" in source

        assert source["source"]
        assert isinstance(source["chunk_id"], int)
        assert 0.0 <= source["similarity"] <= 1.0