from abc import ABC, abstractmethod


class LLMProvider(ABC):
    @abstractmethod
    def generate(self, prompt: str) -> str:
        raise NotImplementedError

    @abstractmethod
    def stream(self, prompt: str):
        raise NotImplementedError

    @abstractmethod
    def structured_output(self, prompt: str, schema: dict) -> dict:
        raise NotImplementedError
