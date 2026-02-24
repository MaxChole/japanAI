"""默认配置：LLM provider、模型名、数据源等。"""
DEFAULT_CONFIG = {
    "llm_provider": "openai",
    "deep_think_llm": "gpt-4o-mini",
    "quick_think_llm": "gpt-4o-mini",
    "backend_url": None,
    "data_vendors": {
        "location_data": "mock",
        "legal_data": "mock",
        "tax_data": "mock",
        "yield_data": "mock",
    },
    "tool_vendors": {},
    "project_dir": ".",
}
