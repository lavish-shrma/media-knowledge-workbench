from datetime import datetime

from sqlalchemy import DateTime
from sqlalchemy import Integer
from sqlalchemy.sql import func
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column

from app.db.base import Base


class ChatConversation(Base):
    __tablename__ = "chat_conversations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
