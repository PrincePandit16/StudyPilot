import uuid
from sqlalchemy import String, Text, Integer, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from src.studypilot.models.base import Base, TimestampMixin, UserOwnedMixin
from datetime import datetime

class FlashcardSet(Base, TimestampMixin, UserOwnedMixin):
    __tablename__ = "flashcard_sets"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    title: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[str | None] = mapped_column(Text)

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="flashcard_sets")
    cards: Mapped[list["Flashcard"]] = relationship("Flashcard", back_populates="flashcard_set", cascade="all, delete-orphan")

class Flashcard(Base, TimestampMixin):
    __tablename__ = "flashcards"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    set_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("flashcard_sets.id", ondelete="CASCADE"), nullable=False, index=True)
    front: Mapped[str] = mapped_column(Text, nullable=False)
    back: Mapped[str] = mapped_column(Text, nullable=False)
    difficulty_level: Mapped[int] = mapped_column(Integer, default=1)

    # Relationships
    flashcard_set: Mapped["FlashcardSet"] = relationship("FlashcardSet", back_populates="cards")

class FlashcardReview(Base, TimestampMixin, UserOwnedMixin):
    __tablename__ = "flashcard_reviews"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    flashcard_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("flashcards.id", ondelete="CASCADE"), nullable=False, index=True)
    rating: Mapped[int] = mapped_column(Integer, nullable=False) # 1-5
    next_review_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    # Relationships
    user: Mapped["User"] = relationship("User")
    flashcard: Mapped["Flashcard"] = relationship("Flashcard")
