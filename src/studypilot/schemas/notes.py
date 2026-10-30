from pydantic import BaseModel, Field
from typing import List, Optional
from uuid import UUID

class ChapterSummary(BaseModel):
    chapter_number: Optional[int] = None
    title: str
    summary: str

class KeyConcept(BaseModel):
    concept: str
    explanation: str
    level: str # "Beginner", "Intermediate", "Advanced"

class Definition(BaseModel):
    term: str
    definition: str

class NoteSchema(BaseModel):
    title: str
    overview: str
    chapters: List[ChapterSummary] = Field(default_factory=list)
    key_concepts: List[KeyConcept] = Field(default_factory=list)
    definitions: List[Definition] = Field(default_factory=list)
    examples: List[str] = Field(default_factory=list)
    revision_points: List[str] = Field(default_factory=list)
    important_questions: List[str] = Field(default_factory=list)
    source_references: List[str] = Field(default_factory=list)
