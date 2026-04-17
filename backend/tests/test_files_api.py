from io import BytesIO

from tests.conftest import client


def test_upload_pdf_and_track_status() -> None:
    response = client.post(
        "/api/v1/files/upload",
        files={"file": ("sample.pdf", BytesIO(b"%PDF-1.4 sample"), "application/pdf")},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["original_name"] == "sample.pdf"
    assert payload["media_kind"] == "document"
    assert payload["status"] == "queued"
    assert payload["size_bytes"] > 0


def test_upload_audio_and_video_are_allowed() -> None:
    audio = client.post(
        "/api/v1/files/upload",
        files={"file": ("clip.mp3", BytesIO(b"id3-audio"), "audio/mpeg")},
    )
    video = client.post(
        "/api/v1/files/upload",
        files={"file": ("movie.mp4", BytesIO(b"video-bytes"), "video/mp4")},
    )

    assert audio.status_code == 200
    assert video.status_code == 200
    assert audio.json()["media_kind"] == "audio"
    assert video.json()["media_kind"] == "video"


def test_upload_rejects_unsupported_file_type() -> None:
    response = client.post(
        "/api/v1/files/upload",
        files={"file": ("notes.txt", BytesIO(b"plain text"), "text/plain")},
    )

    assert response.status_code == 400
    assert response.json()["detail"].startswith("Unsupported file type")


def test_list_files_and_get_file_by_id() -> None:
    uploaded = client.post(
        "/api/v1/files/upload",
        files={"file": ("manual.pdf", BytesIO(b"%PDF-manual"), "application/pdf")},
    )
    file_id = uploaded.json()["id"]

    listing = client.get("/api/v1/files")
    details = client.get(f"/api/v1/files/{file_id}")

    assert listing.status_code == 200
    assert details.status_code == 200
    assert any(item["id"] == file_id for item in listing.json())
    assert details.json()["original_name"] == "manual.pdf"


def test_get_file_returns_404_for_unknown_id() -> None:
    response = client.get("/api/v1/files/999999")

    assert response.status_code == 404
    assert response.json()["detail"] == "File not found"
