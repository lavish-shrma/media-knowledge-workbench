from datetime import datetime

from pydantic import BaseModel


class FileResponse(BaseModel):
    id: int
    original_name: str
    mime_type: str
    media_kind: str
    status: str
    size_bytes: int
    created_at: datetime

    model_config = {"from_attributes": True}


class ProcessFileResponse(BaseModel):
    file_id: int
    status: str
    summary_model: str
    transcript_segments: int


class SummaryResponse(BaseModel):
    file_id: int
    summary_text: str
    model_name: str


class TranscriptSegmentResponse(BaseModel):
    start_seconds: float
    end_seconds: float
    text: str


class TranscriptResponse(BaseModel):
    file_id: int
    segments: list[TranscriptSegmentResponse]
