"""
统计单次请求内所有 LLM 调用的 token 用量，供 API 返回并在前端展示。
"""
from typing import Any, Dict, Optional

from langchain_core.callbacks import BaseCallbackHandler
from langchain_core.outputs import LLMResult


class TokenUsageCallback(BaseCallbackHandler):
    """在一次图执行中累计所有 LLM 调用的 prompt/completion/total tokens。"""

    def __init__(self) -> None:
        self.prompt_tokens: int = 0
        self.completion_tokens: int = 0
        self.total_tokens: int = 0

    def on_llm_end(self, response: LLMResult, **kwargs: Any) -> None:
        """从 LLMResult 中累加 token 用量（llm_output 或各 generation 的 response_metadata）。"""
        # 优先从 llm_output 取（OpenAI/MiniMax 等）
        if response.llm_output:
            usage = response.llm_output.get("token_usage") or response.llm_output.get("usage")
            if usage:
                self._add_usage(usage)
                return
        # 备选：从每条 message 的 response_metadata 取
        for gen_list in response.generations or []:
            for gen in gen_list:
                if hasattr(gen, "message") and gen.message:
                    meta = getattr(gen.message, "response_metadata", None) or {}
                    u = meta.get("usage_metadata") or meta.get("token_usage") or meta.get("usage")
                    if u:
                        self._add_usage(u)
                        return
                if hasattr(gen, "generation_info") and gen.generation_info:
                    self._add_usage(gen.generation_info)
                    return
                break
            break
        return

    def _add_usage(self, usage: Dict[str, Any]) -> None:
        p = usage.get("prompt_tokens") or usage.get("input_tokens") or 0
        c = usage.get("completion_tokens") or usage.get("output_tokens") or 0
        self.prompt_tokens += int(p)
        self.completion_tokens += int(c)
        self.total_tokens = self.prompt_tokens + self.completion_tokens

    def to_dict(self) -> Dict[str, int]:
        return {
            "prompt_tokens": self.prompt_tokens,
            "completion_tokens": self.completion_tokens,
            "total_tokens": self.total_tokens,
        }
