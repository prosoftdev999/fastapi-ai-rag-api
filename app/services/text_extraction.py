from pathlib import Path

import aiofiles
from pypdf import PdfReader


class TextExtractionError(Exception):
    """Raised when text cannot be extracted from a document."""


async def extract_plain_text(file_path: Path) -> str:
    try:
        async with aiofiles.open(
            file_path,
            "r",
            encoding="utf-8",
            errors="ignore",
        ) as file:
            return await file.read()
    except OSError as exc:
        raise TextExtractionError(f"Could not read file: {file_path.name}") from exc


def extract_pdf_text(file_path: Path) -> str:
    try:
        reader = PdfReader(str(file_path))
    except Exception as exc:
        raise TextExtractionError(f"Could not open PDF file: {file_path.name}") from exc

    page_text: list[str] = []

    for page in reader.pages:
        try:
            text = page.extract_text() or ""
        except Exception:  # noqa: BLE001
            text = ""

        text = text.strip()

        if text:
            page_text.append(text)

    return "\n\n".join(page_text)


async def extract_text(file_path: Path) -> str:
    if not file_path.exists():
        raise TextExtractionError(
            f"Stored document file does not exist: {file_path.name}"
        )

    extension = file_path.suffix.lower()

    if extension in {".txt", ".md"}:
        text = await extract_plain_text(file_path)
    elif extension == ".pdf":
        text = extract_pdf_text(file_path)
    else:
        raise TextExtractionError(f"Unsupported document extension: {extension}")

    cleaned_text = text.strip()

    if not cleaned_text:
        raise TextExtractionError("No readable text was found in the document")

    return cleaned_text
