from dataclasses import dataclass
import math
import re

from sqlalchemy.orm import Session

from app.models.document_chunk import DocumentChunk
from app.models.uploaded_file import UploadedFile
from app.services.embeddings import build_embedding


@dataclass
class RetrievedChunk:
    chunk: DocumentChunk
    score: float


def cosine_similarity(left: list[float], right: list[float]) -> float:
    numerator = sum(a * b for a, b in zip(left, right))
    left_norm = math.sqrt(sum(a * a for a in left)) or 1.0
    right_norm = math.sqrt(sum(b * b for b in right)) or 1.0
    return numerator / (left_norm * right_norm)


def lexical_overlap_bonus(question: str, text: str) -> float:
    question_terms = {term for term in re.findall(r"[a-z0-9]+", question.lower()) if len(term) > 2}
    if not question_terms:
        return 0.0

    text_terms = set(re.findall(r"[a-z0-9]+", text.lower()))
    overlap = len(question_terms & text_terms)
    return min(overlap * 0.12, 0.24)


def retrieve_chunks(
    db: Session,
    question: str,
    file_ids: list[int] | None = None,
    media_kinds: list[str] | None = None,
    min_score: float = 0.0,
    limit: int = 4,
) -> list[RetrievedChunk]:
    query_embedding = build_embedding(question)
    base_query = db.query(DocumentChunk)
    if file_ids:
        base_query = base_query.filter(DocumentChunk.file_id.in_(file_ids))

    if media_kinds:
        media_file_ids = [item.id for item in db.query(UploadedFile.id).filter(UploadedFile.media_kind.in_(media_kinds)).all()]
        base_query = base_query.filter(DocumentChunk.file_id.in_(media_file_ids))

    scored: list[RetrievedChunk] = []
    for chunk in base_query.all():
        vector_score = cosine_similarity(query_embedding, [float(item) for item in chunk.embedding])
        length_bonus = min(len(chunk.text.split()) / 300.0, 0.15)
        time_bonus = 0.0 if chunk.start_seconds is None else 0.05
        score = vector_score + length_bonus + time_bonus + lexical_overlap_bonus(question, chunk.text)
        if score < min_score:
            continue
        scored.append(RetrievedChunk(chunk=chunk, score=score))

    scored.sort(key=lambda item: item.score, reverse=True)
    return scored[:limit]
