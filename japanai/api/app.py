"""
FastAPI 应用：提供 POST /advise 接口，入参为标的、用户画像、可选基准日，
返回最终决策、信号（BUY/HOLD/AVOID）及各报告摘要。
"""
from datetime import date
from typing import Any, Dict, Optional

from fastapi import FastAPI
from pydantic import BaseModel, Field

from japanai.real_estate_graph import RealEstateGraph

app = FastAPI(
    title="JapanAI 地产投资建议",
    description="多角色 Agent 产出 BUY/HOLD/AVOID 及可执行建议",
)

# 全局图实例（可改为依赖注入或按请求创建）
_graph: Optional[RealEstateGraph] = None


def get_graph() -> RealEstateGraph:
    global _graph
    if _graph is None:
        _graph = RealEstateGraph()
    return _graph


class AdviseRequest(BaseModel):
    """请求体：地产标的与用户画像。"""
    property_of_interest: str = Field(..., description="地产标的（区域、楼盘等）")
    user_profile: str = Field(..., description="用户画像：预算、用途、是否非居住者、持有期限等")
    trade_date: Optional[str] = Field(None, description="分析基准日 yyyy-mm-dd，默认今天")


class AdviseResponse(BaseModel):
    """响应：最终决策、信号、及各报告与计划摘要。"""
    signal: str = Field(..., description="BUY | HOLD | AVOID")
    final_decision: str = Field(..., description="风控裁判完整结论")
    investment_plan: str = Field("", description="研究经理投资计划")
    trader_investment_plan: str = Field("", description="交易员可执行计划")
    location_report: str = Field("", description="区域报告摘要")
    legal_report: str = Field("", description="法律报告摘要")
    tax_report: str = Field("", description="税务报告摘要")
    yield_report: str = Field("", description="收益报告摘要")


@app.post("/advise", response_model=AdviseResponse)
def advise(req: AdviseRequest) -> AdviseResponse:
    """
    运行多 Agent 图，返回最终建议与各报告。
    内部会依次执行：区域/法律/税务/收益分析师 → 多空辩论 → 研究经理 → 交易员 → 风控辩论 → 风控裁判。
    """
    graph = get_graph()
    final_state, signal = graph.propagate(
        property_of_interest=req.property_of_interest,
        user_profile=req.user_profile,
        trade_date=req.trade_date,
    )
    return AdviseResponse(
        signal=signal,
        final_decision=final_state.get("final_decision") or "",
        investment_plan=final_state.get("investment_plan") or "",
        trader_investment_plan=final_state.get("trader_investment_plan") or "",
        location_report=final_state.get("location_report") or "",
        legal_report=final_state.get("legal_report") or "",
        tax_report=final_state.get("tax_report") or "",
        yield_report=final_state.get("yield_report") or "",
    )


@app.get("/health")
def health() -> Dict[str, str]:
    return {"status": "ok"}
