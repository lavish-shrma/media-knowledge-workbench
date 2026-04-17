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


class TranscriptSegment(Base):
    __tablename__ = "transcript_segments"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    file_id: Mapped[int] = mapped_column(ForeignKey("uploaded_files.id"), nullable=False, index=True)
    start_seconds: Mapped[float] = mapped_column(Float, nullable=False)
    end_seconds: Mapped[float] = mapped_column(Float, nullable=False)
    text: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
