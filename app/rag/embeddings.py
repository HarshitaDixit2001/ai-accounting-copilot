import httpx

from app.core.config import settings


EMBEDDING_MODEL = "nomic-embed-text:latest"


class EmbeddingServiceError(Exception):
    """Raised when the embedding service fails."""


async def generate_embedding(text: str) -> list[float]:
    if not text.strip():
        raise ValueError("Text cannot be empty")

    url = f"{settings.OLLAMA_BASE_URL}/api/embeddings"

    payload = {
        "model": EMBEDDING_MODEL,
        "prompt": text,
    }

    try:
        async with httpx.AsyncClient(
            timeout=120.0
        ) as client:

            response = await client.post(
                url,
                json=payload,
            )

            response.raise_for_status()

    except httpx.TimeoutException as exc:
        raise EmbeddingServiceError(
            "Embedding request timed out"
        ) from exc

    except httpx.HTTPError as exc:
        raise EmbeddingServiceError(
            "Failed to communicate with embedding service"
        ) from exc

    data = response.json()

    embedding = data.get("embedding")

    if not embedding:
        raise EmbeddingServiceError(
            "Embedding service returned an empty embedding"
        )

    return embedding