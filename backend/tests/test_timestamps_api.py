from io import BytesIO

from tests.conftest import client


def test_extract_timestamps_returns_ranked_matches(monkeypatch) -> None:
    upload = client.post(
        "/api/v1/files/upload",
        files={"file": ("topic.mp3", BytesIO(b"audio-bytes"), "audio/mpeg")},
    )
    file_id = upload.json()["id"]

    monkeypatch.setattr(
        "app.api.v1.files.transcribe_media",
        lambda _path, _model: [
            {"start": 1.0, "end": 4.0, "text": "machine learning overview"},
            {"start": 5.0, "end": 7.0, "text": "database indexing details"},
        ],
    )
    monkeypatch.setattr(
        "app.api.v1.files.summarize_text",
        lambda content: (f"summary::{content}", "fallback:extractive"),
    )

    process = client.post(f"/api/v1/files/{file_id}/process")
    assert process.status_code == 200

    response = client.post(
        "/api/v1/timestamps/extract",
        json={"file_id": file_id, "topic": "machine learning", "limit": 3},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["file_id"] == file_id
    assert payload["matches"]
    assert payload["matches"][0]["start_seconds"] == 1.0


def test_extract_timestamps_rejects_document_file() -> None:
    upload = client.post(
        "/api/v1/files/upload",
        files={"file": ("notes.pdf", BytesIO(b"%PDF-doc"), "application/pdf")},
    )
    file_id = upload.json()["id"]

    response = client.post(
        "/api/v1/timestamps/extract",
        json={"file_id": file_id, "topic": "anything"},
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Timestamp extraction is only available for audio/video"


def test_stream_media_returns_file_for_audio() -> None:
    upload = client.post(
        "/api/v1/files/upload",
        files={"file": ("clip.mp3", BytesIO(b"abc123"), "audio/mpeg")},
    )
    file_id = upload.json()["id"]

    response = client.get(f"/api/v1/media/{file_id}/stream")

    assert response.status_code == 200
    assert response.content == b"abc123"


def test_stream_media_returns_400_for_document() -> None:
    upload = client.post(
        "/api/v1/files/upload",
        files={"file": ("doc.pdf", BytesIO(b"%PDF"), "application/pdf")},
    )
    file_id = upload.json()["id"]

    response = client.get(f"/api/v1/media/{file_id}/stream")

    assert response.status_code == 400
    assert response.json()["detail"] == "Only audio/video files can be streamed"
