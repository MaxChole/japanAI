"""
统一数据流入口：Agent 侧工具只调用 route_to_vendor(method, ...)，
不直接依赖具体数据源；后续可扩展多 vendor 与 fallback。
"""
from .config import get_config
from .mock_vendor import (
    get_location_data as get_location_data_mock,
    get_legal_faq,
    get_policy_faq,
    get_tax_rules,
    get_yield_inputs,
)
from .csv_vendor import get_location_data as get_location_data_csv
from japanai.utils.step_logger import log_skill_used

# 方法名 -> 实现函数（mock / csv 等）
VENDOR_METHODS = {
    "get_location_data": {"mock": get_location_data_mock, "csv": get_location_data_csv},
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

# 东京/日本区域关键词：get_location_data 自动触发 skill 时用，不依赖「是否用 CSV」配置
_TOKYO_REGION_KEYWORDS = (
    "东京", "日本", "港区", "中央区", "千代田区", "新宿区", "渋谷区", "品川区", "目黒区",
    "大田区", "世田谷区", "中野区", "杉並区", "豊島区", "北区", "荒川区", "板橋区", "練馬区",
    "足立区", "葛飾区", "江戸川区", "文京区", "台東区", "墨田区", "江東区",
    "Tokyo", "Minato", "Chuo", "Chiyoda", "Shinjuku", "Shibuya", "Shinagawa", "Meguro",
    "Ota", "Setagaya", "Nakano", "Suginami", "Toshima", "Kita", "Arakawa", "Itabashi",
    "Nerima", "Adachi", "Katsushika", "Edogawa", "Bunkyo", "Taito", "Sumida", "Koto",
)


def _is_tokyo_region(region: str) -> bool:
    """请求区域是否为东京/日本，用于 skill 自动触发：是则读 CSV 给大模型，无需任何配置。"""
    if not region or not isinstance(region, str):
        return False
    r = region.strip()
    return any(kw in r for kw in _TOKYO_REGION_KEYWORDS)


def get_vendor(method: str, *args, **kwargs) -> str:
    """返回该方法实际使用的 vendor。get_location_data 固定由 skill 自动触发：东京/日本→读 CSV，否则 mock，无「用不用 CSV」配置。"""
    if method == "get_location_data":
        region = (args[0] if args else "") or ""
        return "csv" if _is_tokyo_region(region) else "mock"

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
    """根据配置将 method 路由到对应 vendor 并执行。get_location_data 由 skill 自动触发，东京/日本即读 CSV 给大模型。"""
    if method not in VENDOR_METHODS:
        raise ValueError(f"Unsupported method: {method}")
    vendor = get_vendor(method, *args, **kwargs)
    if vendor not in VENDOR_METHODS[method]:
        vendor = "mock"
    if method == "get_location_data" and vendor == "csv":
        log_skill_used("japan-realestate-csv", "get_location_data → CSV (skill 自动触发)")
    impl = VENDOR_METHODS[method][vendor]
    return impl(*args, **kwargs)
