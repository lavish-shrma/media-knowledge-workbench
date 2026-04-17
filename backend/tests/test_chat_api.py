from io import BytesIO

from tests.conftest import client


def test_chat_query_creates_conversation_and_returns_sources(monkeypatch) -> None:
    upload = client.post(
        "/api/v1/files/upload",
        files={"file": ("chat.pdf", BytesIO(b"%PDF-chat"), "application/pdf")},
    )
    file_id = upload.json()["id"]

    monkeypatch.setattr("app.api.v1.files.extract_pdf_text", lambda _path: "Alpha beta gamma delta")
    monkeypatch.setattr(
        "app.api.v1.files.summarize_text",
        lambda content: (f"summary::{content}", "fallback:extractive"),
    )

    process = client.post(f"/api/v1/files/{file_id}/process")
    assert process.status_code == 200

    chat = client.post(
        "/api/v1/chat/query",
        json={"question": "What does the document contain?", "file_ids": [file_id]},
    )

    assert chat.status_code == 200
    payload = chat.json()
    assert payload["conversation_id"] > 0
    assert payload["answer"]
    assert len(payload["sources"]) >= 1

    history = client.get(f"/api/v1/chat/conversations/{payload['conversation_id']}")
    assert history.status_code == 200
    assert len(history.json()["messages"]) == 2


def test_chat_query_handles_missing_conversation() -> None:
    response = client.post(
        "/api/v1/chat/query",
        json={"question": "hello", "conversation_id": 99999},
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Conversation not found"


def test_chat_query_rejects_empty_question() -> None:
    response = client.post(
        "/api/v1/chat/query",
        json={"question": "   "},
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Question cannot be empty"


def test_get_conversation_returns_404_for_unknown_id() -> None:
    response = client.get("/api/v1/chat/conversations/55555")

    assert response.status_code == 404
    assert response.json()["detail"] == "Conversation not found"


def test_chat_sources_include_time_spans_for_media(monkeypatch) -> None:
    upload = client.post(
        "/api/v1/files/upload",
        files={"file": ("voice.mp3", BytesIO(b"audio-bytes"), "audio/mpeg")},
    )
    file_id = upload.json()["id"]

    monkeypatch.setattr(
        "app.api.v1.files.transcribe_media",
        lambda _path, _model: [
            {"start": 2.0, "end": 6.0, "text": "The topic starts here"},
            {"start": 7.0, "end": 9.5, "text": "More details"},
        ],
    )
    monkeypatch.setattr(
        "app.api.v1.files.summarize_text",
        lambda content: (f"summary::{content}", "fallback:extractive"),
    )

    process = client.post(f"/api/v1/files/{file_id}/process")
    assert process.status_code == 200

    chat = client.post(
        "/api/v1/chat/query",
        json={"question": "Where does the topic start?", "file_ids": [file_id]},
    )
    assert chat.status_code == 200

    source = chat.json()["sources"][0]
    assert source["start_seconds"] is not None
    assert source["end_seconds"] is not None
