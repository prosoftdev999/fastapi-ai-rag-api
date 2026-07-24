import re


def normalize_text(text: str) -> str:
    text = text.replace("\x00", "")
    text = re.sub(r"\r\n?", "\n", text)
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)

    return text.strip()


def chunk_text(
    text: str,
    *,
    chunk_size: int = 1000,
    overlap: int = 200,
) -> list[str]:
    if chunk_size <= 0:
        raise ValueError("chunk_size must be greater than zero")

    if overlap < 0:
        raise ValueError("overlap cannot be negative")

    if overlap >= chunk_size:
        raise ValueError("overlap must be smaller than chunk_size")

    normalized = normalize_text(text)

    if not normalized:
        return []

    chunks: list[str] = []
    start = 0
    text_length = len(normalized)

    while start < text_length:
        end = min(start + chunk_size, text_length)

        if end < text_length:
            preferred_break = normalized.rfind("\n\n", start, end)

            if preferred_break <= start:
                preferred_break = normalized.rfind(". ", start, end)

            if preferred_break <= start:
                preferred_break = normalized.rfind(" ", start, end)

            if preferred_break > start + (chunk_size // 2):
                end = preferred_break + 1

        chunk = normalized[start:end].strip()

        if chunk:
            chunks.append(chunk)

        if end >= text_length:
            break

        next_start = end - overlap

        if next_start <= start:
            next_start = end

        start = next_start

    return chunks


def estimate_token_count(text: str) -> int:
    # A simple approximation for portfolio/demo use.
    # English text averages roughly four characters per token.
    return max(1, len(text) // 4)
