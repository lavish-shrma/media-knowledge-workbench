import hashlib
import math

from app.models.document_chunk import DocumentChunk


def _hash_to_unit(value: str) -> float:
    digest = hashlib.sha256(value.encode("utf-8")).hexdigest()[:8]
    return (int(digest, 16) % 1000) / 1000.0


def build_embedding(text: str, dimensions: int = 8) -> list[float]:
    cleaned = " ".join(text.split())
    if not cleaned:
        return [0.0] * dimensions

    vector: list[float] = []
    for index in range(dimensions):
        vector.append(_hash_to_unit(f"{cleaned}:{index}"))

    norm = math.sqrt(sum(item * item for item in vector)) or 1.0
    return [item / norm for item in vector]


def chunk_text(content: str, chunk_size: int = 220) -> list[str]:
    words = content.split()
    if not words:
        return []

    chunks: list[str] = []
    for index in range(0, len(words), chunk_size):
        chunks.append(" ".join(words[index : index + chunk_size]))
    return chunks


def build_chunks_for_file(file_id: int, content: str) -> list[DocumentChunk]:
    chunks = chunk_text(content)
    built: list[DocumentChunk] = []

    for chunk_index, chunk in enumerate(chunks):
        built.append(
            DocumentChunk(
                file_id=file_id,
                chunk_index=chunk_index,
                text=chunk,
                embedding=build_embedding(chunk),
            )
        )

    return built


def build_chunks_for_segments(file_id: int, segments: list[dict[str, float | str]]) -> list[DocumentChunk]:
    built: list[DocumentChunk] = []

    for chunk_index, segment in enumerate(segments):
        text = str(segment.get("text", "")).strip()
        built.append(
            DocumentChunk(
                file_id=file_id,
                chunk_index=chunk_index,
                text=text,
                embedding=build_embedding(text),
                start_seconds=float(segment.get("start", 0.0)),
                end_seconds=float(segment.get("end", 0.0)),
            )
        )

    return built
