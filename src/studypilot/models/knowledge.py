import uuid
from sqlalchemy import String, Text, ARRAY
from sqlalchemy.orm import Mapped, mapped_column, relationship
from src.studypilot.models.base import Base, TimestampMixin, UserOwnedMixin

class Note(Base, TimestampMixin, UserOwnedMixin):
    __tablename__ = "notes"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    title: Mapped[str] = mapped_column(String, nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    tags: Mapped[list[str] | None] = mapped_column(ARRAY(String))

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="notes")
