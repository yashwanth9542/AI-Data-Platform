import json
import urllib.request

from app.core.exceptions import ProviderError
from app.providers.llm.base import LLMProvider


class GeminiProvider(LLMProvider):
    def __init__(self, api_key: str) -> None:
        self.api_key = api_key
        print("[backend] GeminiProvider initialized")

    def generate(self, prompt: str) -> str:
        print(f"[backend] GeminiProvider.generate called with prompt: {prompt}")
        if not self.api_key:
            raise ProviderError("GEMINI_API_KEY is not configured")

        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={self.api_key}"
        payload = {"contents": [{"parts": [{"text": prompt}]}]}
        print(f"[backend] Sending payload to Gemini: {payload}")
        request = urllib.request.Request(
            url,
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        try:
            with urllib.request.urlopen(request, timeout=20) as response:
                body = json.loads(response.read().decode("utf-8"))
                result = body["candidates"][0]["content"]["parts"][0]["text"]
                print("[backend] GeminiProvider.generate received response")
                return result
        except Exception as exc:
            print(f"[backend] GeminiProvider.generate failed: {exc}")
            raise ProviderError(f"Gemini request failed: {exc}") from exc

    def stream(self, prompt: str):
        return iter([self.generate(prompt)])

    def structured_output(self, prompt: str, schema: dict) -> dict:
        return {"provider": "gemini", "prompt": prompt, "schema": schema}
