"""OpenAI 兼容 API 客户端（OpenAI / Ollama / OpenRouter / MiniMax）。支持 429 限流时自动等待重试。"""
import logging
import os
import time
from typing import Any, Optional

from langchain_openai import ChatOpenAI

from .base_client import BaseLLMClient

try:
    from openai import RateLimitError
except ImportError:
    RateLimitError = None  # type: ignore

LOG = logging.getLogger("japanai.steps")

# 429 时等待秒数（RPM 限流通常按分钟重置），重试次数
RATE_LIMIT_WAIT_SEC = 65
RATE_LIMIT_MAX_RETRIES = 4


class ChatOpenAIWithRetry(ChatOpenAI):
    """遇到 429 Rate Limit 时等待后重试，避免整条链路因单次限流失败。"""

    def _generate(self, *args, **kwargs):
        last_error = None
        for attempt in range(RATE_LIMIT_MAX_RETRIES):
            try:
                return super()._generate(*args, **kwargs)
            except Exception as e:
                last_error = e
                is_429 = (
                    (RateLimitError is not None and isinstance(e, RateLimitError))
                    or getattr(e, "http_status", None) == 429
                    or "429" in str(e)
                    or "rate_limit" in str(e).lower()
                )
                if is_429 and attempt < RATE_LIMIT_MAX_RETRIES - 1:
                    LOG.warning(
                        "[JapanAI] LLM 429 限流，%ds 后重试 (%d/%d)",
                        RATE_LIMIT_WAIT_SEC,
                        attempt + 1,
                        RATE_LIMIT_MAX_RETRIES,
                    )
                    time.sleep(RATE_LIMIT_WAIT_SEC)
                    continue
                raise
        raise last_error


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
        # 使用带 429 重试的 LLM，避免 MiniMax 等 RPM 限流导致整条链路 500
        return ChatOpenAIWithRetry(**llm_kwargs)

    def validate_model(self) -> bool:
        return True
