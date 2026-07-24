import pytest

from app.services.chunking import (
    chunk_text,
    estimate_token_count,
    normalize_text,
)


def test_normalize_text() -> None:
    text = "Hello   world\r\n\r\n\r\nNext paragraph."

    result = normalize_text(text)

    assert result == "Hello world\n\nNext paragraph."


def test_short_text_creates_one_chunk() -> None:
    chunks = chunk_text(
        "This is a short document.",
        chunk_size=100,
        overlap=20,
    )

    assert chunks == ["This is a short document."]


def test_long_text_creates_multiple_chunks() -> None:
    text = " ".join(f"word-{index}" for index in range(200))

    chunks = chunk_text(
        text,
        chunk_size=150,
        overlap=30,
    )

    assert len(chunks) > 1
    assert all(chunk for chunk in chunks)


def test_overlap_must_be_smaller_than_chunk_size() -> None:
    with pytest.raises(
        ValueError,
        match="overlap must be smaller",
    ):
        chunk_text(
            "Example text",
            chunk_size=100,
            overlap=100,
        )


def test_estimate_token_count() -> None:
    assert estimate_token_count("12345678") == 2
    assert estimate_token_count("a") == 1
