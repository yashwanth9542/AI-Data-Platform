from app.core.config import settings
from app.core.exceptions import ProviderError
from app.providers.llm.gemini import GeminiProvider
from app.providers.llm.openai import OpenAIProvider


class LLMProviderFactory:
    def create(self, provider_name: str | None = None):
        provider_key = (provider_name or settings.default_llm_provider).lower()
        print(f"[backend] Creating LLM provider: {provider_key}")
        if provider_key == "openai":
            if not settings.openai_api_key:
                raise ProviderError("OPENAI_API_KEY is not configured")
            return OpenAIProvider(api_key=settings.openai_api_key)
        if provider_key == "gemini":
            if not settings.gemini_api_key:
                raise ProviderError("GEMINI_API_KEY is not configured")
            return GeminiProvider(api_key=settings.gemini_api_key)
        raise ProviderError(f"Unsupported LLM provider: {provider_name}")
