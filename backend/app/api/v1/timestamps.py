from pathlib import Path

from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException
from fastapi.responses import FileResponse as FastAPIFileResponse
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.uploaded_file import UploadedFile
from app.schemas.timestamp import TimestampExtractRequest
from app.schemas.timestamp import TimestampExtractResponse
from app.schemas.timestamp import TimestampMatchResponse
from app.services.timestamps import extract_topic_timestamps

router = APIRouter(tags=["timestamps", "media"])


@router.post("/timestamps/extract", response_model=TimestampExtractResponse)
def extract_timestamps(payload: TimestampExtractRequest, db: Session = Depends(get_db)) -> TimestampExtractResponse:
    file_record = db.query(UploadedFile).filter(UploadedFile.id == payload.file_id).first()
    if file_record is None:
        raise HTTPException(status_code=404, detail="File not found")

    if file_record.media_kind not in {"audio", "video"}:
        raise HTTPException(status_code=400, detail="Timestamp extraction is only available for audio/video")

    matches = extract_topic_timestamps(db, file_record.id, payload.topic, payload.limit)

    return TimestampExtractResponse(
        file_id=file_record.id,
        topic=payload.topic,
        matches=[
            TimestampMatchResponse(
                start_seconds=float(item["start_seconds"]),
                end_seconds=float(item["end_seconds"]),
                text=str(item["text"]),
                score=float(item["score"]),
            )
            for item in matches
        ],
    )


@router.get("/media/{file_id}/stream")
def stream_media(file_id: int, db: Session = Depends(get_db)) -> FastAPIFileResponse:
    file_record = db.query(UploadedFile).filter(UploadedFile.id == file_id).first()
    if file_record is None:
        raise HTTPException(status_code=404, detail="File not found")

    if file_record.media_kind not in {"audio", "video"}:
        raise HTTPException(status_code=400, detail="Only audio/video files can be streamed")

    media_path = Path(file_record.local_path)
    if not media_path.exists():
        raise HTTPException(status_code=404, detail="Media file not found on disk")

    return FastAPIFileResponse(path=media_path, media_type=file_record.mime_type, filename=file_record.original_name)
