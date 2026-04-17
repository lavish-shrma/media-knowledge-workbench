from datetime import datetime

from sqlalchemy import DateTime
from sqlalchemy import ForeignKey
from sqlalchemy import Integer
from sqlalchemy import Text
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.sql import func

from app.db.base import Base


class ExtractedDocument(Base):
    __tablename__ = "extracted_documents"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    file_id: Mapped[int] = mapped_column(ForeignKey("uploaded_files.id"), nullable=False, unique=True)
    content_text: Mapped[str] = mapped_column(Text, nullable=False)
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
