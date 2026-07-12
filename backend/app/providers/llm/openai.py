import json
import urllib.request

from app.core.exceptions import ProviderError
from app.providers.llm.base import LLMProvider


class OpenAIProvider(LLMProvider):
    def __init__(self, api_key: str) -> None:
        self.api_key = api_key
        print("[backend] OpenAIProvider initialized")

    def generate(self, prompt: str) -> str:
        print(f"[backend] OpenAIProvider.generate called with prompt: {prompt}")
        if not self.api_key:
            raise ProviderError("OPENAI_API_KEY is not configured")

        payload = {
            "model": "gpt-4o-mini",
            "messages": [{"role": "system", "content": "You are an analytics copilot."}, {"role": "user", "content": prompt}],
            "temperature": 0.2,
        }
        print(f"[backend] Sending payload to OpenAI: {payload}")
        request = urllib.request.Request(
            "https://api.openai.com/v1/chat/completions",
            data=json.dumps(payload).encode("utf-8"),
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            },
            method="POST",
        )
        try:
            with urllib.request.urlopen(request, timeout=20) as response:
                body = json.loads(response.read().decode("utf-8"))
                result = body["choices"][0]["message"]["content"]
                print("[backend] OpenAIProvider.generate received response")
                return result
        except Exception as exc:
            print(f"[backend] OpenAIProvider.generate failed: {exc}")
            raise ProviderError(f"OpenAI request failed: {exc}") from exc

    def stream(self, prompt: str):
        return iter([self.generate(prompt)])

    def structured_output(self, prompt: str, schema: dict) -> dict:
        return {"provider": "openai", "prompt": prompt, "schema": schema}
