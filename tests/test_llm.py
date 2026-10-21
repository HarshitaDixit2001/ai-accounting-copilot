from unittest.mock import AsyncMock, patch
from app.schemas.llm import AccountingResponse
import pytest

from app.services.accounting_service import ask_accounting_assistant


@pytest.mark.asyncio
async def test_accounting_assistant():
    with patch(
        "app.services.accounting_service.generate_response",
        new_callable=AsyncMock,
        return_value="A journal entry records a financial transaction using debit and credit.",
    ):
        response = await ask_accounting_assistant(
            "What is a journal entry?"
        )

    assert response.answer
    assert "journal entry" in response.answer.lower()

@pytest.mark.asyncio
async def test_ollama_service_success():
    mock_response = AsyncMock()
    mock_response.json = lambda: {
        "response": "Test response from Ollama"
    }
    mock_response.raise_for_status = lambda: None

    with patch(
        "httpx.AsyncClient.post",
        new_callable=AsyncMock,
        return_value=mock_response,
    ):
        from app.services.ollama_service import generate_response

        response = await generate_response("Test prompt")

    assert response == "Test response from Ollama"

@pytest.mark.asyncio
async def test_ollama_service_http_error():
    import httpx

    mock_response = AsyncMock()

    mock_response.raise_for_status = lambda: (_ for _ in ()).throw(
        httpx.HTTPStatusError(
            "Server error",
            request=httpx.Request(
                "POST",
                "http://localhost:11434/api/generate",
            ),
            response=httpx.Response(500),
        )
    )

    with patch(
        "httpx.AsyncClient.post",
        new_callable=AsyncMock,
        return_value=mock_response,
    ):
        from app.services.ollama_service import (
            OllamaServiceError,
            generate_response,
        )

        with pytest.raises(OllamaServiceError):
            await generate_response("Test prompt")

@pytest.mark.asyncio
async def test_ollama_service_timeout():
    import httpx

    with patch(
        "httpx.AsyncClient.post",
        new_callable=AsyncMock,
        side_effect=httpx.TimeoutException("Request timed out"),
    ):
        from app.services.ollama_service import (
            OllamaServiceError,
            generate_response,
        )

        with pytest.raises(OllamaServiceError) as exc_info:
            await generate_response("Test prompt")

    assert str(exc_info.value) == "Ollama request timed out"

@pytest.mark.asyncio
async def test_ollama_service_empty_response():
    mock_response = AsyncMock()

    mock_response.json = lambda: {}
    mock_response.raise_for_status = lambda: None

    with patch(
        "httpx.AsyncClient.post",
        new_callable=AsyncMock,
        return_value=mock_response,
    ):
        from app.services.ollama_service import (
            OllamaServiceError,
            generate_response,
        )

        with pytest.raises(OllamaServiceError) as exc_info:
            await generate_response("Test prompt")

    assert str(exc_info.value) == "Ollama returned an empty response"

def test_build_accounting_prompt():
    from app.prompts.accounting import build_accounting_prompt

    question = "What is a journal entry?"

    prompt = build_accounting_prompt(question)

    assert question in prompt
    assert "AI accounting assistant" in prompt
    assert "Debit and Credit" in prompt

@pytest.mark.asyncio
async def test_accounting_assistant_calls_llm():
    expected_response = (
        "Debit the expense account and credit the cash account."
    )

    with patch(
        "app.services.accounting_service.generate_response",
        new_callable=AsyncMock,
        return_value=expected_response,
    ) as mock_generate:

        from app.services.accounting_service import ask_accounting_assistant

        response = await ask_accounting_assistant(
            "How do I record a cash expense?"
        )

    assert response.answer == expected_response

    mock_generate.assert_awaited_once()

    called_prompt = mock_generate.await_args.args[0]

    assert "How do I record a cash expense?" in called_prompt
    assert "AI accounting assistant" in called_prompt

def test_llm_request_rejects_empty_prompt():
    from app.schemas.llm import LLMRequest

    with pytest.raises(ValueError):
        LLMRequest(prompt="")

def test_llm_request_rejects_prompt_over_5000_characters():
    from app.schemas.llm import LLMRequest

    with pytest.raises(ValueError):
        LLMRequest(prompt="A" * 5001)

def test_llm_response_schema():
    from app.schemas.llm import LLMResponse

    response = LLMResponse(
        response="Test accounting response"
    )

    assert response.response == "Test accounting response"

def test_llm_response_rejects_missing_response():
    from app.schemas.llm import LLMResponse

    with pytest.raises(ValueError):
        LLMResponse()

from fastapi.testclient import TestClient
from app.main import app


client = TestClient(app)


def test_accounting_ask_endpoint():
    with patch(
        "app.api.routes.llm.ask_accounting_assistant",
        new_callable=AsyncMock,
        return_value=AccountingResponse(
            answer="A journal entry records a financial transaction.",
        ),
    ):
        response = client.post(
            "/accounting/ask",
            json={
                "prompt": "What is a journal entry?"
            },
        )

    assert response.status_code == 200

    data = response.json()

    assert data["answer"] == (
        "A journal entry records a financial transaction."
    )

def test_llm_request_rejects_empty_prompt():
    response = client.post(
        "/llm/generate",
        json={"prompt": ""},
    )

    assert response.status_code == 422


def test_llm_request_rejects_oversized_prompt():
    response = client.post(
        "/llm/generate",
        json={"prompt": "a" * 5001},
    )

    assert response.status_code == 422