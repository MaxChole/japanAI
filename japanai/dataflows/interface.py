"""
统一数据流入口：Agent 侧工具只调用 route_to_vendor(method, ...)，
不直接依赖具体数据源；后续可扩展多 vendor 与 fallback。
"""
from .config import get_config
from .mock_vendor import (
    get_location_data,
    get_legal_faq,
    get_policy_faq,
    get_tax_rules,
    get_yield_inputs,
)

# 方法名 -> 实现函数（当前仅 mock）
VENDOR_METHODS = {
    "get_location_data": {"mock": get_location_data},
    "get_legal_faq": {"mock": get_legal_faq},
    "get_policy_faq": {"mock": get_policy_faq},
    "get_tax_rules": {"mock": get_tax_rules},
    "get_yield_inputs": {"mock": get_yield_inputs},
}

# 工具分类（供 config 中按 category 配置 vendor）
TOOLS_CATEGORIES = {
    "location_data": {"description": "区域/地段数据", "tools": ["get_location_data"]},
    "legal_data": {"description": "法律/合规", "tools": ["get_legal_faq"]},
    "policy_data": {"description": "户籍国在目标国购房政策", "tools": ["get_policy_faq"]},
    "tax_data": {"description": "税务规则", "tools": ["get_tax_rules"]},
    "yield_data": {"description": "收益/现金流", "tools": ["get_yield_inputs"]},
}


def get_vendor(method: str) -> str:
    """返回该方法配置的 vendor，默认 mock。"""
    config = get_config()
    tool_vendors = config.get("tool_vendors", {})
    if method in tool_vendors:
        return tool_vendors[method]
    data_vendors = config.get("data_vendors", {})
    for cat, info in TOOLS_CATEGORIES.items():
        if method in info["tools"]:
            return data_vendors.get(cat, "mock")
    return "mock"


def route_to_vendor(method: str, *args, **kwargs):
    """根据配置将 method 路由到对应 vendor 实现并执行。"""
    if method not in VENDOR_METHODS:
        raise ValueError(f"Unsupported method: {method}")
    vendor = get_vendor(method)
    if vendor not in VENDOR_METHODS[method]:
        vendor = "mock"  # fallback to mock if configured vendor missing
    impl = VENDOR_METHODS[method][vendor]
    return impl(*args, **kwargs)
