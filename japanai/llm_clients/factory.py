"""根据 provider 创建对应的 LLM 客户端。"""
from typing import Optional
from .base_client import BaseLLMClient
from .openai_client import OpenAIClient


def create_llm_client(
    provider: str,
    model: str,
    base_url: Optional[str] = None,
    **kwargs,
) -> BaseLLMClient:
    """创建 LLM 客户端。provider: openai | ollama | openrouter。"""
    p = provider.lower()
    if p in ("openai", "ollama", "openrouter"):
        return OpenAIClient(model, base_url, provider=p, **kwargs)
    raise ValueError(f"Unsupported LLM provider: {provider}")
