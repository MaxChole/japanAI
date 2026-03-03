"""政策研究员可调用的工具：根据用户户籍/国籍查询在目标国购房政策。"""
from typing import Annotated
from langchain_core.tools import tool
from japanai.dataflows.interface import route_to_vendor


@tool
def get_policy_faq(
    household_region: Annotated[str, "用户户籍/国籍/常居地，如 中国、美国、新加坡"],
    target_country: Annotated[str, "购房目标国"] = "日本",
) -> str:
    """获取「用户户籍国居民」在「目标国」买房的政策与限制要点。"""
    return route_to_vendor("get_policy_faq", household_region, target_country)
