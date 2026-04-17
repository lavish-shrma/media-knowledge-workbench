from io import BytesIO

from tests.conftest import client


def test_process_pdf_creates_summary(monkeypatch) -> None:
    upload = client.post(
        "/api/v1/files/upload",
        files={"file": ("doc.pdf", BytesIO(b"%PDF-sample"), "application/pdf")},
    )
    file_id = upload.json()["id"]

    monkeypatch.setattr("app.api.v1.files.extract_pdf_text", lambda _path: "Alpha Beta Gamma")
    monkeypatch.setattr(
        "app.api.v1.files.summarize_text",
        lambda content: (f"summary::{content}", "openai:gpt-4o-mini"),
    )

    process = client.post(f"/api/v1/files/{file_id}/process")
    summary = client.get(f"/api/v1/files/{file_id}/summary")
    details = client.get(f"/api/v1/files/{file_id}")

    assert process.status_code == 200
    assert process.json()["status"] == "completed"
    assert process.json()["transcript_segments"] == 0
    assert summary.status_code == 200
    assert summary.json()["summary_text"] == "summary::Alpha Beta Gamma"
    assert details.json()["status"] == "completed"


def test_process_audio_creates_transcript_and_summary(monkeypatch) -> None:
    upload = client.post(
        "/api/v1/files/upload",
        files={"file": ("clip.mp3", BytesIO(b"audio"), "audio/mpeg")},
    )
    file_id = upload.json()["id"]

    monkeypatch.setattr(
        "app.api.v1.files.transcribe_media",
        lambda _path, _model: [
            {"start": 1.0, "end": 2.4, "text": "First line"},
            {"start": 3.1, "end": 4.8, "text": "Second line"},
        ],
    )
    monkeypatch.setattr(
        "app.api.v1.files.summarize_text",
        lambda content: (f"summary::{content}", "fallback:extractive"),
    )

    process = client.post(f"/api/v1/files/{file_id}/process")
    transcript = client.get(f"/api/v1/files/{file_id}/transcript")

    assert process.status_code == 200
    assert process.json()["transcript_segments"] == 2
    assert transcript.status_code == 200
    assert len(transcript.json()["segments"]) == 2
    assert transcript.json()["segments"][0]["text"] == "First line"


def test_get_summary_returns_404_when_missing() -> None:
    response = client.get("/api/v1/files/123/summary")

    assert response.status_code == 404
    assert response.json()["detail"] == "Summary not found for file"


def test_process_returns_404_for_unknown_file() -> None:
    response = client.post("/api/v1/files/9999/process")

    assert response.status_code == 404
    assert response.json()["detail"] == "File not found"


def test_process_marks_file_failed_when_pipeline_errors(monkeypatch) -> None:
    upload = client.post(
        "/api/v1/files/upload",
        files={"file": ("broken.pdf", BytesIO(b"%PDF-fail"), "application/pdf")},
    )
    file_id = upload.json()["id"]

    monkeypatch.setattr("app.api.v1.files.extract_pdf_text", lambda _path: "broken")

    def _raise_error(_content):
        raise RuntimeError("summary failure")

    monkeypatch.setattr("app.api.v1.files.summarize_text", _raise_error)

    response = client.post(f"/api/v1/files/{file_id}/process")
    details = client.get(f"/api/v1/files/{file_id}")

    assert response.status_code == 500
    assert response.json()["detail"].startswith("Processing failed")
    assert details.json()["status"] == "failed"
