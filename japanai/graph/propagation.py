"""
初始状态构造与图调用参数：create_initial_state 产出带空报告与初始辩论状态的 state，
get_graph_args 返回 stream_mode、recursion_limit 等。
"""
from typing import Any, Dict, List, Optional

from japanai.agents.utils.agent_states import RealEstateAgentState


# 多空辩论初始状态（需包含 TypedDict 全部键）
def _empty_invest_debate() -> dict:
    return {
        "bull_history": "",
        "bear_history": "",
        "history": "",
        "current_response": "",
        "judge_decision": "",
        "count": 0,
    }


# 风控辩论初始状态
def _empty_risk_debate() -> dict:
    return {
        "aggressive_history": "",
        "conservative_history": "",
        "neutral_history": "",
        "history": "",
        "latest_speaker": "",
        "current_aggressive_response": "",
        "current_conservative_response": "",
        "current_neutral_response": "",
        "judge_decision": "",
        "count": 0,
    }


class Propagator:
    def __init__(self, max_recur_limit: int = 100):
        self.max_recur_limit = max_recur_limit

    def create_initial_state(
        self,
        property_of_interest: str,
        user_profile: str,
        trade_date: str,
        household_region: str = "",
    ) -> Dict[str, Any]:
        """构造图的初始 state：消息、标的、用户画像、户籍、空报告、初始辩论状态。"""
        return {
            "messages": [("human", property_of_interest)],
            "property_of_interest": property_of_interest,
            "user_profile": user_profile,
            "household_region": household_region or "",
            "trade_date": trade_date,
            "location_report": "",
            "legal_report": "",
            "policy_report": "",
            "tax_report": "",
            "yield_report": "",
            "investment_debate_state": _empty_invest_debate(),
            "investment_plan": "",
            "trader_investment_plan": "",
            "risk_debate_state": _empty_risk_debate(),
            "final_decision": "",
        }

    def get_graph_args(self, callbacks: Optional[List] = None) -> Dict[str, Any]:
        """返回 graph.invoke/stream 的参数字典。"""
        config = {"recursion_limit": self.max_recur_limit}
        if callbacks:
            config["callbacks"] = callbacks
        return {"stream_mode": "values", "config": config}
