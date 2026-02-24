"""法律/合规分析师可调用的工具。"""
from typing import Annotated
from langchain_core.tools import tool
from japanai.dataflows.interface import route_to_vendor


@tool
def get_legal_faq(
    is_non_resident: Annotated[bool, "是否为非居住者（外国人等）"],
    purpose: Annotated[str, "用途：自住 或 投资"],
) -> str:
    """获取与外国人购房、产权、租赁法规等相关的要点摘要。"""
    return route_to_vendor("get_legal_faq", is_non_resident, purpose)
