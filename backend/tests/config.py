import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    app_name: str = "AI Data Platform"
    log_level: str = os.getenv("LOG_LEVEL", "INFO")
    openai_api_key: str | None = os.getenv("OPENAI_API_KEY")
    gemini_api_key: str | None = os.getenv("GEMINI_API_KEY")
    grok_api_key: str | None = os.getenv("GROK_API_KEY")
    default_llm_provider: str = "groq"
    default_database: str = os.getenv("DEFAULT_DATABASE", "mysql")
    postgres_dsn: str | None = os.getenv("POSTGRES_DSN")
    mysql_dsn: str | None = os.getenv("MYSQL_DSN")
    sqlite_path: str = os.getenv("SQLITE_PATH", "./data/analytics.db")
    groq_api_key: str | None = os.getenv("GROQ_API_KEY")
    groq_model: str = os.getenv(
        "GROQ_MODEL",
        "openai/gpt-oss-120b"
    )

settings = Settings()
