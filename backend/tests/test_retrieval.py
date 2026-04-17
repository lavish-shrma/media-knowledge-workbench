from app.services.embeddings import build_chunks_for_file
from app.services.embeddings import build_chunks_for_segments
from app.services.embeddings import build_embedding
from app.services.embeddings import chunk_text
from app.services.retrieval import cosine_similarity


def test_chunk_text_splits_content() -> None:
    words = " ".join(["token"] * 500)
    chunks = chunk_text(words, chunk_size=200)

    assert len(chunks) == 3


def test_build_embedding_is_normalized() -> None:
    vector = build_embedding("normalized vector")
    magnitude = sum(item * item for item in vector)

    assert 0.99 <= magnitude <= 1.01


def test_build_chunks_for_file_serializes_embedding() -> None:
    chunks = build_chunks_for_file(11, "hello world this is a chunk")

    assert len(chunks) == 1
    assert chunks[0].file_id == 11
    assert len(chunks[0].embedding) == 8


def test_build_chunks_for_segments_keeps_spans() -> None:
    chunks = build_chunks_for_segments(
        22,
        [{"start": 1.0, "end": 2.5, "text": "segment text"}],
    )

    assert len(chunks) == 1
    assert chunks[0].start_seconds == 1.0
    assert chunks[0].end_seconds == 2.5


def test_cosine_similarity_identity() -> None:
    vector = [0.1, 0.2, 0.3]
    assert cosine_similarity(vector, vector) == 1.0
