from datetime import datetime
from enum import Enum

from sqlalchemy import DateTime
from sqlalchemy import Enum as SqlEnum
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy.sql import func
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column

from app.db.base import Base


class FileStatus(str, Enum):
    queued = "queued"
    processing = "processing"
    completed = "completed"
    failed = "failed"


class UploadedFile(Base):
    __tablename__ = "uploaded_files"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    original_name: Mapped[str] = mapped_column(String(255), nullable=False)
    stored_name: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    mime_type: Mapped[str] = mapped_column(String(100), nullable=False)
    media_kind: Mapped[str] = mapped_column(String(20), nullable=False)
    local_path: Mapped[str] = mapped_column(String(500), nullable=False)
    size_bytes: Mapped[int] = mapped_column(Integer, nullable=False)
    status: Mapped[FileStatus] = mapped_column(
        SqlEnum(FileStatus, name="file_status"),
        nullable=False,
        default=FileStatus.queued,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )
