from datetime import datetime

from sqlalchemy import DateTime
from sqlalchemy import Float
from sqlalchemy import ForeignKey
from sqlalchemy import Index
from sqlalchemy import Integer
from sqlalchemy import JSON
from sqlalchemy import Text
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.sql import func
from pgvector.sqlalchemy import Vector

from app.db.base import Base


class DocumentChunk(Base):
    __tablename__ = "document_chunks"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    file_id: Mapped[int] = mapped_column(ForeignKey("uploaded_files.id"), nullable=False, index=True)
    chunk_index: Mapped[int] = mapped_column(Integer, nullable=False)
    text: Mapped[str] = mapped_column(Text, nullable=False)
    embedding: Mapped[list[float]] = mapped_column(Vector(8).with_variant(JSON, "sqlite"), nullable=False)
    start_seconds: Mapped[float | None] = mapped_column(Float, nullable=True)
    end_seconds: Mapped[float | None] = mapped_column(Float, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )


Index(
    "ix_document_chunks_embedding_cosine",
    DocumentChunk.embedding,
    postgresql_using="ivfflat",
    postgresql_ops={"embedding": "vector_cosine_ops"},
)
