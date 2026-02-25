"""默认配置：LLM provider、模型名、API Key、数据源、辩论轮数等。"""
DEFAULT_CONFIG = {
    "llm_provider": "openai",
    "deep_think_llm": "gpt-4o-mini",
    "quick_think_llm": "gpt-4o-mini",
    "api_key": None,
    "backend_url": None,
    "data_vendors": {
        "location_data": "mock",
        "legal_data": "mock",
        "tax_data": "mock",
        "yield_data": "mock",
    },
    "tool_vendors": {},
    "project_dir": ".",
    "max_debate_rounds": 1,
    "max_risk_discuss_rounds": 1,
}
