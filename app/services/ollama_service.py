
import logging
import time
from typing import TypedDict

import httpx
from fastapi.responses import JSONResponse

from app.core.config import settings
from app.core.exceptions import OllamaServiceError

logger = logging.getLogger(__name__)


class GenerationResult(TypedDict):
    response: str
    model: str
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int
    latency_ms: float
    ollama_duration_ms: float


async def generate_response_with_metadata(
    prompt: str,
    model: str | None = None,
) -> GenerationResult:
    selected_model = model or settings.OLLAMA_MODEL
    url = f"{settings.OLLAMA_BASE_URL}/api/generate"

    payload = {
        "model": selected_model,
        "prompt": prompt,
        "stream": False,
        "think": False,
        "options": {"num_predict": 400},
    }

    start_time = time.perf_counter()

    try:
        async with httpx.AsyncClient(timeout=300.0) as client:
            response = await client.post(url, json=payload)
            response.raise_for_status()
            data = response.json()

    except httpx.TimeoutException as exc:
        logger.error(
            "Ollama request timed out | model=%s",
            selected_model,
        )
        raise OllamaServiceError(
            "Ollama request timed out"
        ) from exc

    except httpx.HTTPError as exc:
        logger.error(
            "Ollama HTTP request failed | model=%s | error=%s",
            selected_model,
            exc,
        )
        raise OllamaServiceError(
            "Failed to communicate with Ollama"
        ) from exc

    latency_ms = (time.perf_counter() - start_time) * 1000

    generated_text = data.get("response")
    prompt_tokens = data.get("prompt_eval_count", 0) or 0
    completion_tokens = data.get("eval_count", 0) or 0
    total_duration_ns = data.get("total_duration", 0) or 0

    if not generated_text:
        logger.error(
            "Ollama returned an empty response | model=%s",
            selected_model,
        )
        raise OllamaServiceError(
            "Ollama returned an empty response"
        )

    result: GenerationResult = {
        "response": generated_text,
        "model": selected_model,
        "prompt_tokens": prompt_tokens,
        "completion_tokens": completion_tokens,
        "total_tokens": prompt_tokens + completion_tokens,
        "latency_ms": round(latency_ms, 2),
        "ollama_duration_ms": round(
            total_duration_ns / 1_000_000, 2
        ),
    }

    logger.info(
        "Ollama generation completed | model=%s | "
        "prompt_tokens=%s | completion_tokens=%s | "
        "latency_ms=%.2f",
        selected_model,
        prompt_tokens,
        completion_tokens,
        latency_ms,
    )

    return result


async def generate_response(
    prompt: str,
    model: str | None = None,
) -> str:
    result = await generate_response_with_metadata(
        prompt,
        model=model,
    )
    return result["response"]


async def ollama_service_error_handler(
    request: httpx.Request,
    exc: OllamaServiceError,
):
    return JSONResponse(
        status_code=503,
        content={
            "error": "ollama_service_unavailable",
            "message": exc.message,
        },
    )
