from datetime import datetime

from pydantic import BaseModel


class ChatQueryRequest(BaseModel):
    question: str
    conversation_id: int | None = None
    file_ids: list[int] | None = None
    media_kinds: list[str] | None = None
    min_score: float = 0.0
    limit: int = 4


class ChatSourceResponse(BaseModel):
    file_id: int
    chunk_id: int
    source_text: str
    score: float
    start_seconds: float | None = None
    end_seconds: float | None = None


class ChatAnswerResponse(BaseModel):
    conversation_id: int
    answer: str
    model_name: str
    sources: list[ChatSourceResponse]


class ChatMessageResponse(BaseModel):
    role: str
    content: str
    created_at: datetime

    model_config = {"from_attributes": True}


class ConversationHistoryResponse(BaseModel):
    conversation_id: int
    messages: list[ChatMessageResponse]
