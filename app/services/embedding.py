from openai import AsyncOpenAI, OpenAIError

from app.core.config import settings


class EmbeddingError(Exception):
    """Raised when an embedding cannot be generated."""


client = AsyncOpenAI(api_key=settings.openai_api_key)


async def create_embedding(text: str) -> list[float]:
    if not text.strip():
        raise EmbeddingError("Cannot create an embedding for empty text")

    try:
        response = await client.embeddings.create(
            model=settings.embedding_model,
            input=text,
            dimensions=settings.embedding_dimension,
        )
    except OpenAIError as exc:
        raise EmbeddingError("OpenAI embedding request failed") from exc

    if not response.data:
        raise EmbeddingError("OpenAI returned no embedding data")

    embedding = response.data[0].embedding

    if len(embedding) != settings.embedding_dimension:
        raise EmbeddingError(
            "Embedding dimension does not match application configuration"
        )

    return embedding


async def create_embeddings(
    texts: list[str],
) -> list[list[float]]:
    if not texts:
        return []

    if any(not text.strip() for text in texts):
        raise EmbeddingError("Embedding input contains an empty text chunk")

    try:
        response = await client.embeddings.create(
            model=settings.embedding_model,
            input=texts,
            dimensions=settings.embedding_dimension,
        )
    except OpenAIError as exc:
        raise EmbeddingError("OpenAI embedding batch request failed") from exc

    ordered_data = sorted(
        response.data,
        key=lambda item: item.index,
    )

    embeddings = [item.embedding for item in ordered_data]

    if len(embeddings) != len(texts):
        raise EmbeddingError("OpenAI returned an unexpected number of embeddings")

    for embedding in embeddings:
        if len(embedding) != settings.embedding_dimension:
            raise EmbeddingError("Embedding dimension does not match configuration")

    return embeddings
