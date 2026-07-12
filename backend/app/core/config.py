import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    app_name: str = "AI Data Platform"
    log_level: str = os.getenv("LOG_LEVEL", "INFO")
    openai_api_key: str | None = os.getenv("OPENAI_API_KEY","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")
    gemini_api_key: str | None = os.getenv("GEMINI_API_KEY")
    default_llm_provider: str = os.getenv("DEFAULT_LLM_PROVIDER", "openai")
    default_database: str = os.getenv("DEFAULT_DATABASE", "mysql")
    postgres_dsn: str | None = os.getenv("POSTGRES_DSN")
    mysql_dsn: str | None = os.getenv("MYSQL_DSN")
    sqlite_path: str = os.getenv("SQLITE_PATH", "./data/analytics.db")


settings = Settings()
