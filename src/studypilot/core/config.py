from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional

class Settings(BaseSettings):
    PROJECT_NAME: str = "StudyPilot"
    DATABASE_URL: str
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    GOOGLE_API_KEY: Optional[str] = None

    # Embedding Configuration
    EMBEDDING_MODEL_NAME: str = "all-MiniLM-L6-v2"
    EMBEDDING_DIMENSIONS: int = 384
    SIMILARITY_THRESHOLD: float = 0.5
    TOP_K: int = 5

    # LLM Configuration
    LLM_PROVIDER: str = "groq"  # options: groq, gemini, mock
    GROQ_API_KEY: Optional[str] = None
    GROQ_MODEL: str = "llama-3.3-70b-versatile"
    GEMINI_API_KEY: Optional[str] = None
    LLM_TIMEOUT: int = 30
    LLM_MAX_RETRIES: int = 3
    LLM_TEMPERATURE: float = 0.7

    model_config = SettingsConfigDict(env_file=".env")

settings = Settings()
