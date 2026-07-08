from app.providers.llm.base import LLMProvider


class OpenAIProvider(LLMProvider):
    def generate(self, prompt: str) -> str:
        return f"OpenAI placeholder response for: {prompt}"

    def stream(self, prompt: str):
        return iter([self.generate(prompt)])

    def structured_output(self, prompt: str, schema: dict) -> dict:
        return {"prompt": prompt, "schema": schema}
