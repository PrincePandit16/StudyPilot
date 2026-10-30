import logging
import json
from typing import Type, TypeVar, Any
from pydantic import BaseModel
from src.studypilot.core.llm.base import LLMProvider, LLMResponse, UsageMetadata, HealthStatus

T = TypeVar("T", bound=BaseModel)
logger = logging.getLogger(__name__)

class MockProvider(LLMProvider):
    """A deterministic provider for unit testing."""

    def generate_text(self, prompt: str, **kwargs) -> LLMResponse:
        logger.info(f"[MockProvider] Generating text for prompt: {prompt[:50]}...")
        return LLMResponse(
            text="This is a mocked response from the LLM provider.",
            usage=UsageMetadata(prompt_tokens=10, completion_tokens=20, total_tokens=30),
            model_name="mock-llm-v1"
        )

    def generate_structured(self, prompt: str, response_model: Type[T], **kwargs) -> T:
        logger.info(f"[MockProvider] Generating structured response for: {prompt[:50]}...")

        # In a real mock, we might parse the prompt to return specific data.
        # Here we create a generic instance of the model with dummy data.
        # This assumes the model has a way to be instantiated with default/dummy data.
        # For simplicity, we use a dummy JSON string that matches typical Pydantic models.

        # This is a naive mock; in actual tests, we'd customize this based on the prompt.
        dummy_data = {k: "mocked_value" for k in response_model.model_fields.keys()}
        return response_model.model_validate(dummy_data)

    def get_health_status(self) -> HealthStatus:
        return HealthStatus(is_healthy=True, latency=0.01)
