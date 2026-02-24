"""收益/现金流分析师可调用的工具。"""
from typing import Annotated
from langchain_core.tools import tool
from japanai.dataflows.interface import route_to_vendor


@tool
def get_yield_inputs(
    rent_monthly: Annotated[float, "月租金（日元）"],
    price: Annotated[float, "售价/评估价（日元）"],
    management_fee_ratio: Annotated[float, "管理费占租金比例，如 0.05 表示 5%"] = 0.05,
    vacancy_ratio: Annotated[float, "空置率假设，如 0.05 表示 5%"] = 0.05,
) -> str:
    """根据租金、售价、管理费与空置率计算表面/净回报率等收益数据。"""
    return route_to_vendor(
        "get_yield_inputs",
        rent_monthly,
        price,
        management_fee_ratio=management_fee_ratio,
        vacancy_ratio=vacancy_ratio,
    )
