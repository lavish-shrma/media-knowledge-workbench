from io import BytesIO

from tests.conftest import client


def test_stream_chat_returns_sse_events(monkeypatch) -> None:
    upload = client.post(
        "/api/v1/files/upload",
        files={"file": ("stream.pdf", BytesIO(b"%PDF-stream"), "application/pdf")},
    )
    file_id = upload.json()["id"]

    monkeypatch.setattr("app.api.v1.files.extract_pdf_text", lambda _path: "stream content")
    monkeypatch.setattr(
        "app.api.v1.files.summarize_text",
        lambda content: (f"summary::{content}", "fallback:extractive"),
    )
    assert client.post(f"/api/v1/files/{file_id}/process").status_code == 200

    response = client.get(
        "/api/v1/chat/stream",
        params={"question": "what is in the stream file?", "file_ids": str(file_id)},
    )

    assert response.status_code == 200
    assert "text/event-stream" in response.headers["content-type"]
    assert b"event: chunk" in response.content
    assert b"event: done" in response.content


def test_stream_chat_rejects_empty_question() -> None:
    response = client.get("/api/v1/chat/stream", params={"question": "   "})

    assert response.status_code == 400
    assert response.json()["detail"] == "Question cannot be empty"
