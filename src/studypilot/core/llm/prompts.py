from dataclasses import dataclass
from typing import Dict

@dataclass
class PromptTemplate:
    system_prompt: str
    user_template: str

class StudyPrompts:
    """Centralized repository for all StudyPilot LLM prompts."""

    # Question Answering
    QA = PromptTemplate(
        system_prompt="You are an expert academic assistant. Use the provided context to answer the user's question accurately and concisely.",
        user_template="Context:\n{context}\n\nQuestion: {question}"
    )

    # Summarization
    SUMMARIZATION = PromptTemplate(
        system_prompt="You are a professional summarizer. Create a comprehensive yet concise summary of the provided text, highlighting key concepts and takeaways.",
        user_template="Text to summarize:\n{text}"
    )

    # Quiz Generation
    QUIZ_GEN = PromptTemplate(
        system_prompt="You are an instructional designer. Generate a high-quality quiz based on the provided text. Ensure questions vary in difficulty and target key learning objectives.",
        user_template="Text:\n{text}\n\nGenerate a quiz with {count} multiple-choice questions at {difficulty} difficulty. Return in JSON format with the following structure: \n[\n  {{\n    \"question_text\": \"...\",\n    \"options\": [\"A\", \"B\", \"C\", \"D\"],\n    \"correct_answer\": \"the exact string from options\",\n    \"explanation\": \"...\",\n    \"difficulty\": \"{difficulty}\"\n  }}\n]"
    )

    # Flashcard Generation
    FLASHCARD_GEN = PromptTemplate(
        system_prompt="You are a memory expert. Create effective flashcards using the active recall and spaced repetition principles.",
        user_template="Text:\n{text}\n\nGenerate 10 flashcards (Front/Back). Return in JSON format."
    )

    # Study Planning
    STUDY_PLAN = PromptTemplate(
        system_prompt="You are a study coach. Create a personalized study plan based on the user's goals and the provided material.",
        user_template="Goal: {goal}\nMaterial: {material}\n\nCreate a 1-week study plan."
    )
