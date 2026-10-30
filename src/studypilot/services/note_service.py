import json
from typing import List, Optional
from uuid import UUID
from sqlalchemy.orm import Session
from src.studypilot.repositories.note_repository import NoteRepository
from src.studypilot.core.graph.orchestrator import create_studypilot_graph
from src.studypilot.core.llm.provider import get_llm_provider
from src.studypilot.schemas.notes import NoteSchema
from src.studypilot.services.embedding_service import embedding_service

class NoteService:
    def __init__(self, db_session: Session):
        self.db_session = db_session
        self.repo = NoteRepository(db_session)
        self.graph = create_studypilot_graph()

    async def generate_smart_notes(self, user_id: UUID, document_ids: List[UUID]) -> dict:
        """
        Generates comprehensive smart notes for the given documents.
        """
        llm = get_llm_provider()

        # 1. Retrieve all relevant content from documents
        from src.studypilot.repositories.document_repository import DocumentRepository
        doc_repo = DocumentRepository(self.db_session)

        # For summaries, we want broader context. We'll retrieve chunks for these documents.
        # Since we might have many chunks, we'll take a representative sample or use a summarized approach.
        # For this implementation, we'll fetch top-K most representative chunks.
        all_chunks = []
        for doc_id in document_ids:
            # Using a generic query to get chunks for the document
            # In a real system, we might have a `get_all_chunks_for_document` method
            # Here we use a mock search for "summarize" to get key parts
            query_emb = embedding_service.generate_embedding("main themes and key concepts")
            results = doc_repo.search_similar_chunks(user_id, query_emb, [doc_id], limit=20)
            all_chunks.extend([c.content for c, d in results])

        context = "\n\n".join(all_chunks)

        # 2. Generate Structured Notes using the LLM
        # We request a JSON response matching the NoteSchema
        prompt = f"""
        Analyze the following document content and generate comprehensive study notes.

        Requirements:
        - Title: A concise and descriptive title.
        - Overview: A high-level summary of the material.
        - Chapters: Breakdown the content into logical chapters/sections.
        - Key Concepts: Identify important concepts and provide explanations for Beginner, Intermediate, and Advanced levels.
        - Definitions: Extract key terms and their definitions.
        - Examples: Provide practical, real-world examples.
        - Revision Points: Create a bulleted list of key points for quick review.
        - Important Questions: List critical questions a student should be able to answer.
        - Source References: List the sources used.

        Output MUST be a valid JSON object matching this structure:
        {{
            "title": "...",
            "overview": "...",
            "chapters": [{{ "chapter_number": 1, "title": "...", "summary": "..." }}],
            "key_concepts": [{{ "concept": "...", "explanation": "...", "level": "..." }}],
            "definitions": [{{ "term": "...", "definition": "..." }}],
            "examples": ["..."],
            "revision_points": ["..."],
            "important_questions": ["..."],
            "source_references": ["..."]
        }}

        Content:
        {context}
        """

        response_text = await llm.generate(
            prompt=prompt,
            system_prompt="You are an expert academic note-taker. Output only valid JSON."
        )

        try:
            # Basic JSON cleaning in case LLM adds markdown blocks
            if "```json" in response_text:
                response_text = response_text.split("```json")[1].split("```")[0].strip()
            elif "```" in response_text:
                response_text = response_text.split("```")[1].split("```")[0].strip()

            data = json.loads(response_text)
            validated_notes = NoteSchema(**data)

            # Persist to database
            note = self.repo.create_note(
                user_id=user_id,
                title=validated_notes.title,
                content=validated_notes.json(), # Store as JSON string
                tags=["auto-generated", "smart-notes"]
            )

            return {"id": note.id, **validated_notes.dict()}
        except Exception as e:
            # Fallback or error handling
            return {"error": f"Failed to generate structured notes: {str(e)}", "raw": response_text}

    async def get_note(self, note_id: UUID, user_id: UUID) -> Optional[dict]:
        note = self.repo.get_note(note_id, user_id)
        if not note:
            return None

        try:
            content = json.loads(note.content)
            return {"id": note.id, "title": note.title, "content": content, "tags": note.tags}
        except:
            return {"id": note.id, "title": note.title, "content": note.content, "tags": note.tags}

    async def list_notes(self, user_id: UUID) -> List[dict]:
        notes = self.repo.list_user_notes(user_id)
        return [{"id": n.id, "title": n.title, "tags": n.tags} for n in notes]

    async def delete_note(self, note_id: UUID, user_id: UUID) -> bool:
        return self.repo.delete_note(note_id, user_id)

    async def export_as_markdown(self, note_id: UUID, user_id: UUID) -> str:
        note_data = await self.get_note(note_id, user_id)
        if not note_data:
            raise ValueError("Note not found")

        content = note_data["content"]
        if not isinstance(content, dict):
            return f"# {note_data['title']}\n\n{content}"

        md = [f"# {content.get('title', 'Smart Notes')}\n"]
        md.append(f"## Overview\n{content.get('overview', '')}\n")

        if content.get('chapters'):
            md.append("## Chapters")
            for ch in content['chapters']:
                md.append(f"### {ch.get('title', 'Chapter')}\n{ch.get('summary', '')}\n")

        if content.get('key_concepts'):
            md.append("## Key Concepts")
            for kc in content['key_concepts']:
                md.append(f"- **{kc.get('concept', '')}** ({kc.get('level', 'General')}): {kc.get('explanation', '')}")
            md.append("")

        if content.get('definitions'):
            md.append("## Definitions")
            for df in content['definitions']:
                md.append(f"- **{df.get('term', '')}**: {df.get('definition', '')}")
            md.append("")

        if content.get('examples'):
            md.append("## Practical Examples\n" + "\n".join([f"- {ex}" for ex in content['examples']]) + "\n")

        if content.get('revision_points'):
            md.append("## Revision Points\n" + "\n".join([f"- {rp}" for rp in content['revision_points']]) + "\n")

        if content.get('important_questions'):
            md.append("## Important Questions\n" + "\n".join([f"- {iq}" for iq in content['important_questions']]) + "\n")

        if content.get('source_references'):
            md.append("## Source References\n" + "\n".join([f"- {sr}" for sr in content['source_references']]) + "\n")

        return "\n".join(md)
