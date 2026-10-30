from typing import Any, Dict, List, Optional
from abc import ABC, abstractmethod
import logging
from src.studypilot.core.config import settings

logger = logging.getLogger(__name__)

class LLMProvider(ABC):
    """
    Abstract base class for LLM providers.
    """
    @abstractmethod
    async def generate(self, prompt: str, system_prompt: str = "You are a helpful assistant.", **kwargs) -> str:
        pass

    @abstractmethod
    async def classify(self, text: str, categories: List[str], system_prompt: str = "Classify the following text.") -> str:
        pass

class MockLLMProvider(LLMProvider):
    """
    Mock LLM for testing without API keys.
    """
    async def generate(self, prompt: str, system_prompt: str = "You are a helpful assistant.", **kwargs) -> str:
        return f"[MOCK RESPONSE] Based on prompt: {prompt[:50]}... \n\nAnswer: This is a simulated response."

    async def classify(self, text: str, categories: List[str], system_prompt: str = "Classify the following text.") -> str:
        # Simple mock classification logic
        if "quiz" in text.lower(): return "quiz"
        if "summary" in text.lower(): return "summary"
        if "flashcard" in text.lower(): return "flashcards"
        if "study plan" in text.lower(): return "study_plan"
        return "rag"

class GroqLLMProvider(LLMProvider):
    """
    Groq LLM implementation.
    """
    def __init__(self):
        from groq import Groq
        self.client = Groq(api_key=settings.GROQ_API_KEY)
        self.model = settings.GROQ_MODEL

    async def generate(self, prompt: str, system_prompt: str = "You are a helpful assistant.", **kwargs) -> str:
        import asyncio
        # Groq client is synchronous, wrapping in run_in_executor
        loop = asyncio.get_event_loop()
        completion = await loop.run_in_executor(
            None,
            lambda: self.client.chat.completions.create(
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt}
                ],
                temperature=settings.LLM_TEMPERATURE,
                **kwargs
            )
        )
        return completion.choices[0].message.content

    async def classify(self, text: str, categories: List[str], system_prompt: str = "Classify the following text.") -> str:
        prompt = f"Categories: {', '.join(categories)}\nText: {text}\n\nClassify into one of the categories. Return ONLY the category name."
        return await self.generate(prompt, system_prompt)

class GeminiLLMProvider(LLMProvider):
    """
    Gemini LLM implementation.
    """
    def __init__(self):
        import google.generativeai as genai
        genai.configure(api_key=settings.GEMINI_API_KEY)
        self.model = genai.GenerativeModel(settings.GROQ_MODEL) # Should use Gemini model name here

    async def generate(self, prompt: str, system_prompt: str = "You are a helpful assistant.", **kwargs) -> str:
        import asyncio
        # Gemini SDK is often sync, wrapping as well
        loop = asyncio.get_event_loop()
        response = await loop.run_in_executor(
            None,
            lambda: self.model.generate_content(
                f"System: {system_prompt}\n\nUser: {prompt}"
            )
        )
        return response.text

    async def classify(self, text: str, categories: List[str], system_prompt: str = "Classify the following text.") -> str:
        prompt = f"Categories: {', '.join(categories)}\nText: {text}\n\nClassify into one of the categories. Return ONLY the category name."
        return await self.generate(prompt, system_prompt)

def get_llm_provider() -> LLMProvider:
    """
    Factory to get the configured LLM provider.
    """
    provider = settings.LLM_PROVIDER
    if provider == "groq":
        return GroqLLMProvider()
    elif provider == "gemini":
        return GeminiLLMProvider()
    else:
        return MockLLMProvider()
