from io import BytesIO

from tests.conftest import client


def test_chat_query_filters_by_media_kind(monkeypatch) -> None:
    doc_upload = client.post(
        "/api/v1/files/upload",
        files={"file": ("doc.pdf", BytesIO(b"%PDF-doc"), "application/pdf")},
    )
    audio_upload = client.post(
        "/api/v1/files/upload",
        files={"file": ("clip.mp3", BytesIO(b"audio"), "audio/mpeg")},
    )
    doc_id = doc_upload.json()["id"]
    audio_id = audio_upload.json()["id"]

    monkeypatch.setattr("app.api.v1.files.extract_pdf_text", lambda _path: "Document only content")
    monkeypatch.setattr("app.api.v1.files.transcribe_media", lambda _path, _model: [{"start": 1.0, "end": 2.0, "text": "Audio target topic"}])
    monkeypatch.setattr("app.api.v1.files.summarize_text", lambda content: (f"summary::{content}", "fallback:extractive"))

    assert client.post(f"/api/v1/files/{doc_id}/process").status_code == 200
    assert client.post(f"/api/v1/files/{audio_id}/process").status_code == 200

    response = client.post(
        "/api/v1/chat/query",
        json={
            "question": "topic",
            "file_ids": [doc_id, audio_id],
            "media_kinds": ["audio"],
            "min_score": 0.0,
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["sources"]
    assert all(source["file_id"] == audio_id for source in payload["sources"])


def test_chat_query_respects_min_score(monkeypatch) -> None:
    upload = client.post(
        "/api/v1/files/upload",
        files={"file": ("docs.pdf", BytesIO(b"%PDF"), "application/pdf")},
    )
    file_id = upload.json()["id"]

    monkeypatch.setattr("app.api.v1.files.extract_pdf_text", lambda _path: "tiny")
    monkeypatch.setattr("app.api.v1.files.summarize_text", lambda content: (f"summary::{content}", "fallback:extractive"))
    assert client.post(f"/api/v1/files/{file_id}/process").status_code == 200

    response = client.post(
        "/api/v1/chat/query",
        json={
            "question": "unrelated question",
            "file_ids": [file_id],
            "min_score": 1.5,
        },
    )

    assert response.status_code == 200
    assert response.json()["sources"] == []
