"""
图状态定义：为 LangGraph 与各 Agent 节点提供统一的 state 结构。

- InvestDebateState：多空辩论（Bull/Bear）的 history、count、current_response、judge_decision 等。
- RiskDebateState：风控辩论（激进/保守/中性）的 history、各方 current_*_response、latest_speaker 等。
- RealEstateAgentState：全局 state，包含标的、用户画像、四类报告、辩论状态、投资计划与最终决策。
"""
from typing import Annotated, TypedDict
from langgraph.graph import MessagesState


# ---------- 多空辩论状态 ----------
# 由 Bull/Bear 研究员节点更新，由 Research Manager 消费并写出 judge_decision
class InvestDebateState(TypedDict):
    bull_history: Annotated[str, "Bull 方辩论历史"]
    bear_history: Annotated[str, "Bear 方辩论历史"]
    history: Annotated[str, "完整辩论历史"]
    current_response: Annotated[str, "当前最后一轮发言（供下一轮对方引用）"]
    judge_decision: Annotated[str, "研究经理的裁决与投资计划摘要"]
    count: Annotated[int, "当前辩论轮数（每方发言算一轮）"]


# ---------- 风控辩论状态 ----------
# 由 Aggressive/Conservative/Neutral 节点更新，由 Risk Manager 消费并写出 judge_decision
class RiskDebateState(TypedDict):
    aggressive_history: Annotated[str, "激进方辩论历史"]
    conservative_history: Annotated[str, "保守方辩论历史"]
    neutral_history: Annotated[str, "中性方辩论历史"]
    history: Annotated[str, "完整风控辩论历史"]
    latest_speaker: Annotated[str, "上一轮发言者（Aggressive/Conservative/Neutral）"]
    current_aggressive_response: Annotated[str, "激进方最新发言"]
    current_conservative_response: Annotated[str, "保守方最新发言"]
    current_neutral_response: Annotated[str, "中性方最新发言"]
    judge_decision: Annotated[str, "风控裁判的最终决策"]
    count: Annotated[int, "风控辩论轮数"]


# ---------- 全局图状态 ----------
# 所有节点读写此结构（或其中子字段）；与 TradingAgents 的 AgentState 一一对应，仅字段名改为地产场景
class RealEstateAgentState(MessagesState):
    # 标的与上下文
    property_of_interest: Annotated[str, "用户关心的地产标的（如区域、楼盘名）"]
    user_profile: Annotated[str, "用户画像：预算、用途（自住/投资）、是否非居住者、持有期限等"]
    trade_date: Annotated[str, "分析基准日（yyyy-mm-dd）"]

    # 四类分析师产出（对应股票场景的 market/sentiment/news/fundamentals）
    location_report: Annotated[str, "区域/地段分析报告"]
    legal_report: Annotated[str, "法律/合规报告"]
    tax_report: Annotated[str, "税务报告"]
    yield_report: Annotated[str, "现金流/收益分析报告"]

    # 多空辩论与研究经理产出
    investment_debate_state: Annotated[
        InvestDebateState, "当前多空辩论状态"
    ]
    investment_plan: Annotated[str, "研究经理给出的投资计划摘要"]

    # 交易员产出（供风控辩论与风控裁判使用）
    trader_investment_plan: Annotated[str, "交易员给出的可执行计划；须含 FINAL RECOMMENDATION: BUY/HOLD/AVOID"]

    # 风控辩论与最终决策
    risk_debate_state: Annotated[RiskDebateState, "风控辩论状态"]
    final_decision: Annotated[str, "风控裁判的最终决策（BUY/HOLD/AVOID + 理由）"]
