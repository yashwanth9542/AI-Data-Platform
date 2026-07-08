import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    app_name: str = "AI Data Platform"
    log_level: str = os.getenv("LOG_LEVEL", "INFO")
    openai_api_key: str | None = os.getenv("OPENAI_API_KEY")
    gemini_api_key: str | None = os.getenv("GEMINI_API_KEY")
    default_llm_provider: str = os.getenv("DEFAULT_LLM_PROVIDER", "openai")
    default_database: str = os.getenv("DEFAULT_DATABASE", "sqlite")


settings = Settings()
