from datetime import datetime

from sqlalchemy import DateTime
from sqlalchemy import Float
from sqlalchemy import ForeignKey
from sqlalchemy import Integer
from sqlalchemy import Text
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.sql import func

from app.db.base import Base


class ChatSource(Base):
    __tablename__ = "chat_sources"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    message_id: Mapped[int] = mapped_column(ForeignKey("chat_messages.id"), nullable=False, index=True)
    file_id: Mapped[int] = mapped_column(ForeignKey("uploaded_files.id"), nullable=False, index=True)
    chunk_id: Mapped[int] = mapped_column(ForeignKey("document_chunks.id"), nullable=False)
    source_text: Mapped[str] = mapped_column(Text, nullable=False)
    score: Mapped[float] = mapped_column(Float, nullable=False)
    start_seconds: Mapped[float | None] = mapped_column(Float, nullable=True)
    end_seconds: Mapped[float | None] = mapped_column(Float, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
