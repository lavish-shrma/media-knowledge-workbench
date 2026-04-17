from sqlalchemy.orm import Session

from app.models.transcript_segment import TranscriptSegment


def _tokenize(text: str) -> list[str]:
    return [item.strip().lower() for item in text.split() if item.strip()]


def extract_topic_timestamps(db: Session, file_id: int, topic: str, limit: int = 5) -> list[dict[str, float | str]]:
    segments = (
        db.query(TranscriptSegment)
        .filter(TranscriptSegment.file_id == file_id)
        .order_by(TranscriptSegment.start_seconds.asc())
        .all()
    )

    if not segments:
        return []

    topic_tokens = _tokenize(topic)
    if not topic_tokens:
        return []

    ranked: list[dict[str, float | str]] = []
    for segment in segments:
        lowered = segment.text.lower()
        match_count = sum(1 for token in topic_tokens if token in lowered)
        if match_count == 0:
            continue

        score = match_count / len(topic_tokens)
        ranked.append(
            {
                "start_seconds": float(segment.start_seconds),
                "end_seconds": float(segment.end_seconds),
                "text": segment.text,
                "score": score,
            }
        )

    ranked.sort(key=lambda item: item["score"], reverse=True)

    if ranked:
        return ranked[: max(limit, 1)]

    fallback = segments[0]
    return [
        {
            "start_seconds": float(fallback.start_seconds),
            "end_seconds": float(fallback.end_seconds),
            "text": fallback.text,
            "score": 0.0,
        }
    ]
