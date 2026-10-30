import uuid
from sqlalchemy import String, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from src.studypilot.models.base import Base, TimestampMixin, UserOwnedMixin
import enum

class DocumentStatus(enum.Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    INDEXED = "indexed"

class Document(Base, TimestampMixin, UserOwnedMixin):
    __tablename__ = "documents"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    filename: Mapped[str] = mapped_column(String, nullable=False)
    storage_path: Mapped[str] = mapped_column(String, nullable=False)
    status: Mapped[DocumentStatus] = mapped_column(Enum(DocumentStatus), default=DocumentStatus.PENDING)

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="documents")
    chunks: Mapped[list["DocumentChunk"]] = relationship("DocumentChunk", back_populates="document", cascade="all, delete-orphan")
