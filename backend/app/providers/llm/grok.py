import json
import urllib.request

from app.core.exceptions import ProviderError
from app.providers.llm.base import LLMProvider


class GrokProvider(LLMProvider):
    def __init__(self, api_key: str) -> None:
        self.api_key = api_key
        print("[backend] GrokProvider initialized: ", api_key)

    def generate(self, prompt: str) -> str:
        print(f"[backend] GrokProvider.generate called with prompt: {prompt}")
        if not self.api_key:
            raise ProviderError("GROK_API_KEY is not configured")

        payload = {
            "model": "grok-4.20-0309-reasoning",
            "messages": [{"role": "system", "content": "You are an analytics copilot."}, {"role": "user", "content": prompt}],
            "temperature": 0.2,
        }
        print(f"[backend] Sending payload to Grok: {payload}")
        request = urllib.request.Request(
            "https://api.x.ai/v1/chat/completions",
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
                print("[backend] GrokProvider.generate received response: ", result[10])
                return result
        except urllib.error.HTTPError as e:
            error_body = e.read().decode("utf-8")
            print("Status:", e.code)
            print("Response:", error_body)
            raise ProviderError(f"Grok request failed: {error_body}") from e

    def stream(self, prompt: str):
        return iter([self.generate(prompt)])

    def structured_output(self, prompt: str, schema: dict) -> dict:
        return {"provider": "grok", "prompt": prompt, "schema": schema}
