import logging
from abc import ABC, abstractmethod
from typing import List, Optional, Type, TypeVar, Any
from pydantic import BaseModel
from dataclasses import dataclass

logger = logging.getLogger(__name__)

T = TypeVar("T", bound=BaseModel)

@dataclass
class UsageMetadata:
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0

@dataclass
class LLMResponse:
    text: str
    usage: UsageMetadata
    model_name: str
    raw_response: Any = None

@dataclass
class HealthStatus:
    is_healthy: bool
    latency: Optional[float] = None
    error_message: Optional[str] = None

class LLMProvider(ABC):
    """Abstract Base Class for LLM Providers."""

    @abstractmethod
    def generate_text(self, prompt: str, **kwargs) -> LLMResponse:
        """Generates a simple text response."""
        pass

    @abstractmethod
    def generate_structured(self, prompt: str, response_model: Type[T], **kwargs) -> T:
        """Generates a response that adheres to a Pydantic model."""
        pass

    @abstractmethod
    def get_health_status(self) -> HealthStatus:
        """Checks if the provider is operational."""
        pass
