import hashlib
from pathlib import Path
import shutil
import uuid

from fastapi import APIRouter
from fastapi import Depends
from fastapi import File
from fastapi import HTTPException
from fastapi import UploadFile
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.db.session import get_db
from app.models.extracted_document import ExtractedDocument
from app.models.file_summary import FileSummary
from app.models.transcript_segment import TranscriptSegment
from app.models.uploaded_file import FileStatus
from app.models.uploaded_file import UploadedFile
from app.schemas.file import FileResponse
from app.schemas.file import ProcessFileResponse
from app.schemas.file import SummaryResponse
from app.schemas.file import TranscriptResponse
from app.schemas.file import TranscriptSegmentResponse
from app.services.pdf_extractor import extract_pdf_text
from app.services.embeddings import build_chunks_for_file
from app.services.embeddings import build_chunks_for_segments
from app.services.summarizer import summarize_text
from app.services.transcription import transcribe_media
from app.models.document_chunk import DocumentChunk
from app.models.user import User
from app.services.auth import get_current_user
from app.services.redis_store import cache_get_json
from app.services.redis_store import cache_key
from app.services.redis_store import cache_set_json
from app.services.redis_store import increment_rate_limit
from app.services.redis_store import rate_limit_key

router = APIRouter(prefix="/files", tags=["files"])

ALLOWED_EXTENSIONS = {
    ".pdf": "document",
    ".mp3": "audio",
    ".wav": "audio",
    ".m4a": "audio",
    ".aac": "audio",
    ".ogg": "audio",
    ".mp4": "video",
    ".mov": "video",
    ".avi": "video",
    ".mkv": "video",
    ".webm": "video",
}


def _resolve_media_kind(filename: str) -> str:
    suffix = Path(filename).suffix.lower()
    if suffix not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail="Unsupported file type. Allowed: PDF, audio, video.",
        )
    return ALLOWED_EXTENSIONS[suffix]


@router.post("/upload", response_model=FileResponse)
def upload_file(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> UploadedFile:
    settings = get_settings()
    if increment_rate_limit(rate_limit_key("upload", current_user.email)) > settings.rate_limit_per_minute:
        raise HTTPException(status_code=429, detail="Upload rate limit exceeded")

    media_kind = _resolve_media_kind(file.filename)
    upload_dir = Path(settings.uploads_dir)
    upload_dir.mkdir(parents=True, exist_ok=True)

    file.file.seek(0)
    file_bytes = file.file.read()
    checksum = hashlib.sha256(file_bytes).hexdigest()
    cached = cache_get_json(cache_key("upload", checksum))
    if cached is not None:
        file_record = db.query(UploadedFile).filter(UploadedFile.id == cached["id"]).first()
        if file_record is not None:
            return file_record

    file.file.seek(0)

    stored_name = f"{uuid.uuid4().hex}{Path(file.filename).suffix.lower()}"
    destination = upload_dir / stored_name

    with destination.open("wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    size_bytes = destination.stat().st_size

    record = UploadedFile(
        original_name=file.filename,
        stored_name=stored_name,
        mime_type=file.content_type or "application/octet-stream",
        media_kind=media_kind,
        local_path=str(destination),
        size_bytes=size_bytes,
        status=FileStatus.queued,
    )

    db.add(record)
    db.commit()
    db.refresh(record)

    cache_set_json(
        cache_key("upload", checksum),
        {"id": record.id},
        settings.upload_cache_ttl_seconds,
    )

    return record


@router.get("", response_model=list[FileResponse])
def list_files(db: Session = Depends(get_db)) -> list[UploadedFile]:
    return db.query(UploadedFile).order_by(UploadedFile.created_at.desc()).all()


@router.get("/{file_id}", response_model=FileResponse)
def get_file(file_id: int, db: Session = Depends(get_db)) -> UploadedFile:
    file_record = db.query(UploadedFile).filter(UploadedFile.id == file_id).first()
    if not file_record:
        raise HTTPException(status_code=404, detail="File not found")
    return file_record


@router.post("/{file_id}/process", response_model=ProcessFileResponse)
def process_file(file_id: int, db: Session = Depends(get_db)) -> ProcessFileResponse:
    file_record = db.query(UploadedFile).filter(UploadedFile.id == file_id).first()
    if not file_record:
        raise HTTPException(status_code=404, detail="File not found")

    settings = get_settings()
    file_record.status = FileStatus.processing
    db.commit()

    try:
        content_text = ""
        segments_count = 0

        if file_record.media_kind == "document":
            content_text = extract_pdf_text(file_record.local_path)
            extracted = db.query(ExtractedDocument).filter(ExtractedDocument.file_id == file_record.id).first()
            if extracted is None:
                extracted = ExtractedDocument(file_id=file_record.id, content_text=content_text)
                db.add(extracted)
            else:
                extracted.content_text = content_text
        else:
            segments = transcribe_media(file_record.local_path, settings.whisper_model)
            db.query(TranscriptSegment).filter(TranscriptSegment.file_id == file_record.id).delete()
            for segment in segments:
                db.add(
                    TranscriptSegment(
                        file_id=file_record.id,
                        start_seconds=float(segment["start"]),
                        end_seconds=float(segment["end"]),
                        text=str(segment["text"]),
                    )
                )
            content_text = " ".join(str(segment["text"]) for segment in segments).strip()
            segments_count = len(segments)

        summary_text, model_name = summarize_text(content_text)

        db.query(DocumentChunk).filter(DocumentChunk.file_id == file_record.id).delete()
        if file_record.media_kind == "document":
            built_chunks = build_chunks_for_file(file_record.id, content_text)
        else:
            built_chunks = build_chunks_for_segments(file_record.id, segments)

        for chunk in built_chunks:
            db.add(chunk)

        summary = db.query(FileSummary).filter(FileSummary.file_id == file_record.id).first()
        if summary is None:
            summary = FileSummary(file_id=file_record.id, summary_text=summary_text, model_name=model_name)
            db.add(summary)
        else:
            summary.summary_text = summary_text
            summary.model_name = model_name

        file_record.status = FileStatus.completed
        db.commit()
    except Exception as exc:
        file_record.status = FileStatus.failed
        db.commit()
        raise HTTPException(status_code=500, detail=f"Processing failed: {exc}") from exc

    return ProcessFileResponse(
        file_id=file_record.id,
        status=file_record.status.value,
        summary_model=summary.model_name,
        transcript_segments=segments_count,
    )


@router.get("/{file_id}/summary", response_model=SummaryResponse)
def get_summary(file_id: int, db: Session = Depends(get_db)) -> SummaryResponse:
    summary = db.query(FileSummary).filter(FileSummary.file_id == file_id).first()
    if not summary:
        raise HTTPException(status_code=404, detail="Summary not found for file")

    return SummaryResponse(file_id=file_id, summary_text=summary.summary_text, model_name=summary.model_name)


@router.get("/{file_id}/transcript", response_model=TranscriptResponse)
def get_transcript(file_id: int, db: Session = Depends(get_db)) -> TranscriptResponse:
    segments = (
        db.query(TranscriptSegment)
        .filter(TranscriptSegment.file_id == file_id)
        .order_by(TranscriptSegment.start_seconds.asc())
        .all()
    )

    return TranscriptResponse(
        file_id=file_id,
        segments=[
            TranscriptSegmentResponse(
                start_seconds=segment.start_seconds,
                end_seconds=segment.end_seconds,
                text=segment.text,
            )
            for segment in segments
        ],
    )
