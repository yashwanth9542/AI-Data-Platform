import json
import urllib.error
import urllib.request

from app.core.exceptions import ProviderError
from app.providers.llm.base import LLMProvider
import app.core.config as config

class GroqProvider(LLMProvider):
    def __init__(
        self,
        api_key: str,
        model: str = config.settings.groq_model,
    ) -> None:
        self.api_key = api_key
        self.model = model
        print(f"[backend] GroqProvider initialized (model={self.model}), api_key={api_key}")

    def generate(self, prompt: str) -> str:
        print(f"[backend] GroqProvider.generate called")

        if not self.api_key:
            raise ProviderError("GROQ_API_KEY is not configured")

        payload = {
            "model": self.model,
            "messages": [
                {
                    "role": "system",
                    "content": "You are an analytics copilot."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "temperature": 0,
            "max_tokens": 80,
            "top_p": 1,
            "stream": False,
            "reasoning_effort": "low"
        }

        import json
        import urllib.request
        import urllib.error

        request = urllib.request.Request(
            url="https://api.groq.com/openai/v1/chat/completions",
            data=json.dumps(payload).encode("utf-8"),
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
                "Accept": "application/json",
                "User-Agent": "python-requests/2.31.0",  # anything non-default works
            },
            method="POST",
        )

        try:
            with urllib.request.urlopen(request, timeout=30) as response:
                body = response.read().decode("utf-8")
        except urllib.error.HTTPError as exc:
            error_body = exc.read().decode("utf-8")
            print(f"[backend] Groq API error {exc.code}: {error_body}")
            raise

        data = json.loads(body)
        print(f"[backend] Groq API response: {data}")
        try:
            return data["choices"][0]["message"]["content"]
        except (KeyError, IndexError) as exc:
            print(f"[backend] Unexpected Groq response shape: {data}")
            raise ProviderError(f"Unexpected Groq API response shape: {exc}") from data
        
    def stream(self, prompt: str):
        # V1 placeholder
        return iter([self.generate(prompt)])

    def structured_output(self, prompt: str, schema: dict) -> dict:
        # V1 placeholder
        return {
            "provider": "groq",
            "response": self.generate(prompt),
        }