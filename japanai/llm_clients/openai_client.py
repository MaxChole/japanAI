"""OpenAI 兼容 API 客户端（OpenAI / Ollama / OpenRouter）。"""
import os
from typing import Any, Optional
from langchain_openai import ChatOpenAI
from .base_client import BaseLLMClient


class OpenAIClient(BaseLLMClient):
    def __init__(
        self,
        model: str,
        base_url: Optional[str] = None,
        provider: str = "openai",
        **kwargs,
    ):
        super().__init__(model, base_url, **kwargs)
        self.provider = provider.lower()

    def get_llm(self) -> Any:
        llm_kwargs = {"model": self.model}
        if self.provider == "openrouter":
            llm_kwargs["base_url"] = "https://openrouter.ai/api/v1"
            if os.environ.get("OPENROUTER_API_KEY"):
                llm_kwargs["api_key"] = os.environ["OPENROUTER_API_KEY"]
        elif self.provider == "ollama":
            llm_kwargs["base_url"] = "http://localhost:11434/v1"
            llm_kwargs["api_key"] = "ollama"
        elif self.base_url:
            llm_kwargs["base_url"] = self.base_url
        for key in ("timeout", "max_retries", "api_key", "callbacks"):
            if key in self.kwargs:
                llm_kwargs[key] = self.kwargs[key]
        return ChatOpenAI(**llm_kwargs)

    def validate_model(self) -> bool:
        return True
