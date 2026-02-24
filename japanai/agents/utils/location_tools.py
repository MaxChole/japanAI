"""区域/地段分析师可调用的工具：内部通过 dataflows.route_to_vendor 拉取数据。"""
from typing import Annotated
from langchain_core.tools import tool
from japanai.dataflows.interface import route_to_vendor


@tool
def get_location_data(
    region: Annotated[str, "区域名称，如 东京都港区、大阪市北区"],
    purpose: Annotated[str, "用途：自住 或 投资"],
) -> str:
    """获取指定区域的地段/交通/人口等数据，用于区域分析报告。"""
    return route_to_vendor("get_location_data", region, purpose)
