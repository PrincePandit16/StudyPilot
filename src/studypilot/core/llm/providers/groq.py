import logging
from typing import Type, TypeVar, Any
from pydantic import BaseModel
from groq import Groq
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from src.studypilot.core.llm.base import LLMProvider, LLMResponse, UsageMetadata, HealthStatus
from src.studypilot.core.config import settings

T = TypeVar("T", bound=BaseModel)
logger = logging.getLogger(__name__)

class GroqProvider(LLMProvider):
    """Implementation of LLMProvider using the Groq SDK."""

    def __init__(self):
        if not settings.GROQ_API_KEY:
            logger.warning("GROQ_API_KEY not set. GroqProvider will fail on execution.")

        self.client = Groq(api_key=settings.GROQ_API_KEY)
        self.model = settings.GROQ_MODEL

    @retry(
        stop=stop_after_attempt(settings.LLM_MAX_RETRIES),
        wait=wait_exponential(multiplier=1, min=4, max=10),
        retry=retry_if_exception_type(Exception), # In production, refine to specific Groq/HTTP errors
        reraise=True
    )
    def generate_text(self, prompt: str, **kwargs) -> LLMResponse:
        logger.info(f"GroqProvider: Generating text using {self.model}")

        completion = self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            temperature=kwargs.get("temperature", settings.LLM_TEMPERATURE),
            max_tokens=kwargs.get("max_tokens", 1024),
            timeout=settings.LLM_TIMEOUT
        )

        text = completion.choices[0].message.content
        usage = UsageMetadata(
            prompt_tokens=completion.usage.prompt_tokens,
            completion_tokens=completion.usage.completion_tokens,
            total_tokens=completion.usage.total_tokens
        )

        return LLMResponse(text=text, usage=usage, model_name=self.model, raw_response=completion)

    def generate_structured(self, prompt: str, response_model: Type[T], **kwargs) -> T:
        """
        Uses Groq's JSON mode to get a structured response.
        """
        logger.info(f"GroqProvider: Generating structured response ({response_model.__name__})")

        # Append JSON instruction to the prompt
        json_prompt = f"{prompt}\n\nReturn the response as a JSON object matching the following schema: {response_model.model_json_schema()}"

        completion = self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": json_prompt}],
            response_format={"type": "json_object"},
            temperature=kwargs.get("temperature", settings.LLM_TEMPERATURE),
            timeout=settings.LLM_TIMEOUT
        )

        raw_json = completion.choices[0].message.content
        try:
            return response_model.model_validate_json(raw_json)
        except Exception as e:
            logger.error(f"Failed to validate JSON response: {e}. Raw: {raw_json}")
            raise ValueError(f"LLM response did not match schema {response_model.__name__}: {e}")

    def get_health_status(self) -> HealthStatus:
        try:
            # Simple check: try to list models or make a tiny request
            self.client.models.list()
            return HealthStatus(is_healthy=True)
        except Exception as e:
            logger.error(f"GroqProvider health check failed: {e}")
            return HealthStatus(is_healthy=False, error_message=str(e))
