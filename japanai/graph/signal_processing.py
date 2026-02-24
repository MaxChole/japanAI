"""从风控裁判的完整输出文本中抽取 BUY/HOLD/AVOID 决策。"""
from langchain_core.language_models import BaseChatModel


class SignalProcessor:
    def __init__(self, llm: BaseChatModel):
        self.llm = llm

    def process_signal(self, full_signal: str) -> str:
        """从 final_decision 等长文本中抽取仅 BUY、HOLD 或 AVOID 的结论。"""
        if not (full_signal or "").strip():
            return "HOLD"
        messages = [
            (
                "system",
                "You extract the investment decision from the analyst's text. Output only one word: BUY, HOLD, or AVOID. No other text.",
            ),
            ("human", full_signal),
        ]
        out = self.llm.invoke(messages)
        content = (out.content or "").strip().upper()
        if "BUY" in content:
            return "BUY"
        if "AVOID" in content or "SELL" in content:
            return "AVOID"
        return "HOLD"
