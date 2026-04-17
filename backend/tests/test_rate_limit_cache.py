from io import BytesIO

from tests.conftest import client


def test_upload_cache_reuses_existing_record(monkeypatch) -> None:
    upload_one = client.post(
        "/api/v1/files/upload",
        files={"file": ("cached.pdf", BytesIO(b"%PDF-cache"), "application/pdf")},
    )
    first_id = upload_one.json()["id"]

    upload_two = client.post(
        "/api/v1/files/upload",
        files={"file": ("cached.pdf", BytesIO(b"%PDF-cache"), "application/pdf")},
    )
    second_id = upload_two.json()["id"]

    listing = client.get("/api/v1/files")

    assert upload_one.status_code == 200
    assert upload_two.status_code == 200
    assert first_id == second_id
    assert len(listing.json()) == 1


def test_upload_rate_limit_rejects_when_threshold_exceeded(monkeypatch) -> None:
    monkeypatch.setattr("app.api.v1.files.increment_rate_limit", lambda _key, ttl_seconds=60: 999)

    response = client.post(
        "/api/v1/files/upload",
        files={"file": ("limited.pdf", BytesIO(b"%PDF-limit"), "application/pdf")},
    )

    assert response.status_code == 429
    assert response.json()["detail"] == "Upload rate limit exceeded"


def test_chat_cache_skips_recomputation(monkeypatch) -> None:
    upload = client.post(
        "/api/v1/files/upload",
        files={"file": ("cached-chat.pdf", BytesIO(b"%PDF-chat-cache"), "application/pdf")},
    )
    file_id = upload.json()["id"]

    monkeypatch.setattr("app.api.v1.files.extract_pdf_text", lambda _path: "semantic cache content")
    monkeypatch.setattr(
        "app.api.v1.files.summarize_text",
        lambda content: (f"summary::{content}", "fallback:extractive"),
    )
    assert client.post(f"/api/v1/files/{file_id}/process").status_code == 200

    calls = {"count": 0}

    def fake_answer(question, retrieved):
        calls["count"] += 1
        return f"answer::{question}", "fallback:rule-based"

    monkeypatch.setattr("app.api.v1.chat.answer_question", fake_answer)

    first = client.post(
        "/api/v1/chat/query",
        json={"question": "What is cached?", "file_ids": [file_id]},
    )
    second = client.post(
        "/api/v1/chat/query",
        json={"question": "What is cached?", "file_ids": [file_id]},
    )

    assert first.status_code == 200
    assert second.status_code == 200
    assert calls["count"] == 1


def test_chat_rate_limit_rejects_when_threshold_exceeded(monkeypatch) -> None:
    monkeypatch.setattr("app.api.v1.chat.increment_rate_limit", lambda _key, ttl_seconds=60: 999)

    response = client.post(
        "/api/v1/chat/query",
        json={"question": "rate limit please"},
    )

    assert response.status_code == 429
    assert response.json()["detail"] == "Chat rate limit exceeded"
