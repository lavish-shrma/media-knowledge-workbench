from pydantic import BaseModel


class TimestampExtractRequest(BaseModel):
    file_id: int
    topic: str
    limit: int = 5


class TimestampMatchResponse(BaseModel):
    start_seconds: float
    end_seconds: float
    text: str
    score: float


class TimestampExtractResponse(BaseModel):
    file_id: int
    topic: str
    matches: list[TimestampMatchResponse]
