"""
条件边逻辑：决定分析师后是进入 tools 还是 Msg Clear、多空辩论下一跳、
风控辩论下一跳（Bull/Bear/Research Manager；Aggressive/Conservative/Neutral/Risk Judge）。
"""
from japanai.agents.utils.agent_states import RealEstateAgentState


class ConditionalLogic:
    """根据 state 决定图的下一条边。"""

    def __init__(self, max_debate_rounds: int = 1, max_risk_discuss_rounds: int = 1):
        self.max_debate_rounds = max_debate_rounds
        self.max_risk_discuss_rounds = max_risk_discuss_rounds

    # ---------- 分析师：若最后一条消息有 tool_calls 则进 tools_*，否则进 Msg Clear ----------
    def should_continue_location(self, state: RealEstateAgentState) -> str:
        messages = state["messages"]
        if messages and getattr(messages[-1], "tool_calls", None):
            return "tools_location"
        return "Msg Clear Location"

    def should_continue_legal(self, state: RealEstateAgentState) -> str:
        messages = state["messages"]
        if messages and getattr(messages[-1], "tool_calls", None):
            return "tools_legal"
        return "Msg Clear Legal"

    def should_continue_policy(self, state: RealEstateAgentState) -> str:
        messages = state["messages"]
        if messages and getattr(messages[-1], "tool_calls", None):
            return "tools_policy"
        return "Msg Clear Policy"

    def should_continue_tax(self, state: RealEstateAgentState) -> str:
        messages = state["messages"]
        if messages and getattr(messages[-1], "tool_calls", None):
            return "tools_tax"
        return "Msg Clear Tax"

    def should_continue_yield(self, state: RealEstateAgentState) -> str:
        messages = state["messages"]
        if messages and getattr(messages[-1], "tool_calls", None):
            return "tools_yield"
        return "Msg Clear Yield"

    # ---------- 多空辩论：按 count 与 current_response 决定下一跳 ----------
    def should_continue_debate(self, state: RealEstateAgentState) -> str:
        ideb = state["investment_debate_state"]
        if ideb["count"] >= 2 * self.max_debate_rounds:
            return "Research Manager"
        if (ideb.get("current_response") or "").startswith("Bull"):
            return "Bear Researcher"
        return "Bull Researcher"

    # ---------- 风控辩论：按 count 与 latest_speaker 决定下一跳 ----------
    def should_continue_risk_analysis(self, state: RealEstateAgentState) -> str:
        rdeb = state["risk_debate_state"]
        if rdeb["count"] >= 3 * self.max_risk_discuss_rounds:
            return "Risk Judge"
        if (rdeb.get("latest_speaker") or "").startswith("Aggressive"):
            return "Conservative Analyst"
        if (rdeb.get("latest_speaker") or "").startswith("Conservative"):
            return "Neutral Analyst"
        return "Aggressive Analyst"
