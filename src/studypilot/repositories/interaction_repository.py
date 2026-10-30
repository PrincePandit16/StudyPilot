from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import select
from uuid import UUID
from src.studypilot.models.interaction import Conversation, Message

class InteractionRepository:
    def __init__(self, session: Session):
        self.session = session

    def create_conversation(self, user_id: UUID, title: str) -> Conversation:
        conv = Conversation(
            user_id=user_id,
            title=title
        )
        self.session.add(conv)
        self.session.commit()
        self.session.refresh(conv)
        return conv

    def get_conversation(self, conv_id: UUID, user_id: UUID) -> Optional[Conversation]:
        return self.session.execute(
            select(Conversation).where(Conversation.id == conv_id, Conversation.user_id == user_id)
        ).scalar_one_or_none()

    def list_user_conversations(self, user_id: UUID) -> List[Conversation]:
        return self.session.execute(
            select(Conversation).where(Conversation.user_id == user_id).order_by(Conversation.created_at.desc())
        ).scalars().all()

    def create_message(self, conversation_id: UUID, role: str, content: str) -> Message:
        msg = Message(
            conversation_id=conversation_id,
            role=role,
            content=content
        )
        self.session.add(msg)
        self.session.commit()
        self.session.refresh(msg)
        return msg

    def get_messages(self, conversation_id: UUID, limit: int = 50) -> List[Message]:
        return self.session.execute(
            select(Message).where(Message.conversation_id == conversation_id).order_by(Message.created_at.asc()).limit(limit)
        ).scalars().all()

    def delete_conversation(self, conv_id: UUID, user_id: UUID) -> bool:
        conv = self.get_conversation(conv_id, user_id)
        if not conv:
            return False
        self.session.delete(conv)
        self.session.commit()
        return True
