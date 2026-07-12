import json
import urllib.error
import urllib.request

from app.core.exceptions import ProviderError
from app.providers.llm.base import LLMProvider


class GroqProvider(LLMProvider):
    def __init__(
        self,
        api_key: str,
        model: str = "llama-3.3-70b-versatile",
    ) -> None:
        self.api_key = api_key
        self.model = model
        print(f"[backend] GroqProvider initialized (model={self.model})")

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
            "temperature": 0.2,
        }

        request = urllib.request.Request(
            url="https://api.groq.com/openai/v1/chat/completions",
            data=json.dumps(payload).encode("utf-8"),
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            },
            method="POST",
        )

        try:
            with urllib.request.urlopen(request, timeout=30) as response:
                body = json.loads(response.read().decode("utf-8"))

            return body["choices"][0]["message"]["content"]

        except urllib.error.HTTPError as e:
            error_body = e.read().decode("utf-8")
            print(f"[backend] Groq HTTP {e.code}: {error_body}")
            raise ProviderError(f"Groq request failed: {error_body}") from e

        except Exception as e:
            print(f"[backend] Groq request failed: {e}")
            raise ProviderError(str(e)) from e

    def stream(self, prompt: str):
        # V1 placeholder
        return iter([self.generate(prompt)])

    def structured_output(self, prompt: str, schema: dict) -> dict:
        # V1 placeholder
        return {
            "provider": "groq",
            "response": self.generate(prompt),
        }