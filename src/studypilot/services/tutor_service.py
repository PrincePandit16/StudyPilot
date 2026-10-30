from typing import List, Optional
from uuid import UUID
from sqlalchemy.orm import Session
from src.studypilot.repositories.interaction_repository import InteractionRepository
from src.studypilot.core.graph.orchestrator import create_studypilot_graph
from src.studypilot.core.graph.checkpointer import checkpointer
from src.studypilot.core.llm.provider import get_llm_provider

class TutorService:
    def __init__(self, db_session: Session):
        self.db_session = db_session
        self.repo = InteractionRepository(db_session)
        self.graph = create_studypilot_graph()
        self.saver = checkpointer.get_saver()

    async def create_conversation(self, user_id: UUID, title: str) -> dict:
        conv = self.repo.create_conversation(user_id, title)
        return {"id": conv.id, "title": conv.title}

    async def list_conversations(self, user_id: UUID) -> List[dict]:
        convs = self.repo.list_user_conversations(user_id)
        return [{"id": c.id, "title": c.title, "created_at": c.created_at} for c in convs]

    async def get_conversation(self, conv_id: UUID, user_id: UUID) -> Optional[dict]:
        conv = self.repo.get_conversation(conv_id, user_id)
        if not conv:
            return None
        return {"id": conv.id, "title": conv.title}

    async def delete_conversation(self, conv_id: UUID, user_id: UUID) -> bool:
        return self.repo.delete_conversation(conv_id, user_id)

    async def get_messages(self, conv_id: UUID, user_id: UUID) -> List[dict]:
        # Verify ownership
        conv = self.repo.get_conversation(conv_id, user_id)
        if not conv:
            raise PermissionError("Conversation not found or access denied")

        messages = self.repo.get_messages(conv_id)
        return [{"role": m.role, "content": m.content, "timestamp": m.created_at} for m in messages]

    async def send_message(self, user_id: UUID, conv_id: UUID, message: str, document_ids: Optional[List[UUID]] = None) -> dict:
        # 1. Verify ownership
        conv = self.repo.get_conversation(conv_id, user_id)
        if not conv:
            raise PermissionError("Conversation not found or access denied")

        # 2. Persist user message
        self.repo.create_message(conv_id, "user", message)

        # 3. Prepare Graph State
        # We use conversation_id as the thread_id for LangGraph checkpointing
        thread_id = str(conv_id)

        initial_state = {
            "user_id": str(user_id),
            "conversation_id": thread_id,
            "document_ids": [str(d) for d in document_ids] if document_ids else [],
            "user_message": message,
            "db_session": self.db_session,
            "retry_count": 0
        }

        # 4. Invoke Graph
        config = {"configurable": {"thread_id": thread_id}}
        final_state = await self.graph.ainvoke(initial_state, config=config)

        # 5. Extract answer and citations
        answer = final_state.get("generated_content", "I'm sorry, I couldn't generate a response.")
        citations = final_state.get("citations", [])

        # 6. Persist assistant message
        response_content = f"{answer}\n\nCitations: {', '.join(citations)}" if citations else answer
        self.repo.create_message(conv_id, "assistant", response_content)

        return {
            "answer": answer,
            "citations": citations,
            "conversation_id": conv_id
        }
