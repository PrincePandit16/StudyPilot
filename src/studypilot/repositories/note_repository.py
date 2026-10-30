from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import select
from uuid import UUID
from src.studypilot.models.knowledge import Note

class NoteRepository:
    def __init__(self, session: Session):
        self.session = session

    def create_note(self, user_id: UUID, title: str, content: str, tags: Optional[List[str]] = None) -> Note:
        note = Note(
            user_id=user_id,
            title=title,
            content=content,
            tags=tags
        )
        self.session.add(note)
        self.session.commit()
        self.session.refresh(note)
        return note

    def get_note(self, note_id: UUID, user_id: UUID) -> Optional[Note]:
        return self.session.execute(
            select(Note).where(Note.id == note_id, Note.user_id == user_id)
        ).scalar_one_or_none()

    def list_user_notes(self, user_id: UUID) -> List[Note]:
        return self.session.execute(
            select(Note).where(Note.user_id == user_id).order_by(Note.created_at.desc())
        ).scalars().all()

    def delete_note(self, note_id: UUID, user_id: UUID) -> bool:
        note = self.get_note(note_id, user_id)
        if not note:
            return False
        self.session.delete(note)
        self.session.commit()
        return True
