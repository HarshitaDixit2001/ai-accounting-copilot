import logging
import time
from fastapi.responses import JSONResponse
import httpx

from app.core.config import settings
from app.core.exceptions import OllamaServiceError

logger = logging.getLogger(__name__)




async def generate_response(
    prompt: str,
) -> str:

    url = f"{settings.OLLAMA_BASE_URL}/api/generate"

    payload = {
    "model": settings.OLLAMA_MODEL,
    "prompt": prompt,
    "stream": False,
    "think": False,
    "options": {
        "num_predict": 400,
    },
    }
    start_time = time.perf_counter()
    logger.info(
        "Sending request to Ollama model %s",
        settings.OLLAMA_MODEL,
    )

    try:
        async with httpx.AsyncClient(
            timeout=300.0,
        ) as client:

            response = await client.post(
                url,
                json=payload,
            )

            response.raise_for_status()

    except httpx.TimeoutException as exc:
        logger.error(
            "Ollama request timed out",
        )

        raise OllamaServiceError(
            "Ollama request timed out"
        ) from exc

    except httpx.HTTPError as exc:
        logger.error(
            "Ollama HTTP request failed: %s",
            exc,
        )

        raise OllamaServiceError(
            "Failed to communicate with Ollama"
        ) from exc

    data = response.json()

    generated_text = data.get("response")
    duration_ms = (
        time.perf_counter() - start_time
    ) * 1000
    
    logger.info(
        "Ollama generation completed | model=%s | "
        "duration_ms=%.2f",
        settings.OLLAMA_MODEL,
        duration_ms,
    )
    if not generated_text:
        logger.error(
            "Ollama returned an empty response",
        )

        raise OllamaServiceError(
            "Ollama returned an empty response"
        )

    logger.info(
        "Successfully received response from Ollama",
    )

    return generated_text

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