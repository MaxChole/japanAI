"""税务分析师可调用的工具。"""
from typing import Annotated
from langchain_core.tools import tool
from japanai.dataflows.interface import route_to_vendor


@tool
def get_tax_rules(
    purpose: Annotated[str, "用途：自住 或 投资"],
    holding_years: Annotated[str, "预期持有年限，如 5年、长期"],
) -> str:
    """获取固定资产税、所得税、源泉税、折旧等税务规则摘要。"""
    return route_to_vendor("get_tax_rules", purpose, holding_years)
