import logging
from typing import Optional
from src.studypilot.core.config import settings
from src.studypilot.core.llm.base import LLMProvider
from src.studypilot.core.llm.providers.groq import GroqProvider
from src.studypilot.core.llm.providers.mock import MockProvider

logger = logging.getLogger(__name__)

class LLMProviderFactory:
    _instances = {}

    @classmethod
    def get_provider(cls) -> LLMProvider:
        provider_type = settings.LLM_PROVIDER.lower()

        if provider_type in cls._instances:
            return cls._instances[provider_type]

        logger.info(f"Initializing LLM provider: {provider_type}")

        if provider_type == "groq":
            provider = GroqProvider()
        elif provider_type == "mock":
            provider = MockProvider()
        else:
            # Default to mock for safety or raise error
            logger.warning(f"Unsupported provider '{provider_type}', falling back to MockProvider")
            provider = MockProvider()

        cls._instances[provider_type] = provider
        return provider

# Helper for easy access
def get_llm_provider() -> LLMProvider:
    return LLMProviderFactory.get_provider()
