import asyncio
from functools import lru_cache

from sentence_transformers import SentenceTransformer

from app.core.config import settings


class EmbeddingError(Exception):
    """Raised when local embedding generation fails."""


@lru_cache(maxsize=1)
def get_embedding_model() -> SentenceTransformer:
    """Load and cache the local sentence-transformer model."""
    try:
        return SentenceTransformer(settings.embedding_model)
    except Exception as exc:
        raise EmbeddingError("Could not load the local embedding model") from exc


def _encode_texts(texts: list[str]) -> list[list[float]]:
    """Generate embeddings synchronously using the local model."""
    if not texts:
        return []

    try:
        model = get_embedding_model()

        embeddings = model.encode(
            texts,
            normalize_embeddings=True,
            convert_to_numpy=True,
            show_progress_bar=False,
        )
    except Exception as exc:
        raise EmbeddingError("Local embedding generation failed") from exc

    results: list[list[float]] = embeddings.tolist()

    if len(results) != len(texts):
        raise EmbeddingError(
            "The local model returned an unexpected number of embeddings"
        )

    for embedding in results:
        if len(embedding) != settings.embedding_dimension:
            raise EmbeddingError(
                "Local embedding dimension does not match configuration"
            )

    return results


async def create_embedding(text: str) -> list[float]:
    """Generate one local embedding without blocking the event loop."""
    cleaned_text = text.strip()

    if not cleaned_text:
        raise EmbeddingError("Cannot create an embedding for empty text")

    embeddings = await asyncio.to_thread(
        _encode_texts,
        [cleaned_text],
    )

    return embeddings[0]


async def create_embeddings(
    texts: list[str],
) -> list[list[float]]:
    """Generate local embeddings for multiple text chunks."""
    if not texts:
        return []

    cleaned_texts = [text.strip() for text in texts]

    if any(not text for text in cleaned_texts):
        raise EmbeddingError("Embedding input contains an empty text chunk")

    return await asyncio.to_thread(
        _encode_texts,
        cleaned_texts,
    )
