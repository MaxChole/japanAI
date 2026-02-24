"""LLM 客户端抽象基类：子类实现 get_llm() 与 validate_model()。"""
from abc import ABC, abstractmethod
from typing import Any, Optional


class BaseLLMClient(ABC):
    def __init__(self, model: str, base_url: Optional[str] = None, **kwargs):
        self.model = model
        self.base_url = base_url
        self.kwargs = kwargs

    @abstractmethod
    def get_llm(self) -> Any:
        """返回配置好的 LangChain 兼容 LLM 实例。"""
        pass

    @abstractmethod
    def validate_model(self) -> bool:
        """校验当前 provider 是否支持该 model。"""
        pass
