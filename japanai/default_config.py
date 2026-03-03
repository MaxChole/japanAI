"""默认配置：LLM provider、模型名、API Key、数据源、辩论轮数等。默认使用 MiniMax 大模型。"""
import os

# MiniMax：优先使用环境变量 MINIMAX_API_KEY，否则使用下方默认 Token（仅本地/测试用，勿提交敏感值）
_MINIMAX_API_KEY = os.environ.get(
    "MINIMAX_API_KEY",
    "sk-api-VuGHD4pOJenF2O9O9KgW5e9sVgMOHUWGSl1z3povkajkVcHiJ6tPeEFFhgyFyuA3fQBc_Va5fCTTyhPh0tRpgb2IuXYynV77oSAkcC_vhXx7IYOv9oHownA",
)

DEFAULT_CONFIG = {
    "llm_provider": "openai",
    "deep_think_llm": "abab6.5s-chat",
    "quick_think_llm": "abab6.5s-chat",
    "api_key": _MINIMAX_API_KEY,
    "backend_url": "https://api.minimax.chat/v1",
    "data_vendors": {
        "location_data": "mock",
        "legal_data": "mock",
        "policy_data": "mock",
        "tax_data": "mock",
        "yield_data": "mock",
    },
    "tool_vendors": {},
    "project_dir": ".",
    "max_debate_rounds": 1,
    "max_risk_discuss_rounds": 1,
    # True=三方风控辩论(Aggressive/Conservative/Neutral)后裁判；False=仅风控裁判一人评判（省调用、适合限流）
    "use_risk_debate": False,
}
