"""中性风控辩论员：平衡利弊，情景分析。"""
from japanai.agents.utils.agent_states import RealEstateAgentState


def create_neutral_debator(llm):
    def neutral_node(state: RealEstateAgentState) -> dict:
        rdeb = state["risk_debate_state"]
        history = rdeb.get("history", "")
        neu_history = rdeb.get("neutral_history", "")
        cur_agg = rdeb.get("current_aggressive_response", "")
        cur_con = rdeb.get("current_conservative_response", "")
        trader_plan = state["trader_investment_plan"]
        loc, leg, tax, yld = state["location_report"], state["legal_report"], state["tax_report"], state["yield_report"]

        prompt = f"""As the Neutral Risk Analyst, balance pros and cons for this real estate. Challenge both aggressive and conservative views. Trader plan: {trader_plan}
Reports: Location: {loc}; Legal: {leg}; Tax: {tax}; Yield: {yld}
History: {history}. Last aggressive: {cur_agg}. Last conservative: {cur_con}. If none, just present your view. Debate concisely, no special formatting."""

        response = llm.invoke(prompt)
        argument = f"Neutral Analyst: {response.content}"
        new_rdeb = {
            "history": history + "\n" + argument,
            "aggressive_history": rdeb.get("aggressive_history", ""),
            "conservative_history": rdeb.get("conservative_history", ""),
            "neutral_history": neu_history + "\n" + argument,
            "latest_speaker": "Neutral",
            "current_aggressive_response": rdeb.get("current_aggressive_response", ""),
            "current_conservative_response": rdeb.get("current_conservative_response", ""),
            "current_neutral_response": argument,
            "judge_decision": rdeb.get("judge_decision", ""),
            "count": rdeb["count"] + 1,
        }
        return {"risk_debate_state": new_rdeb}

    return neutral_node
