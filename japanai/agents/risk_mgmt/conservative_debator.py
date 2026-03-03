"""保守风控辩论员：强调流动性、税负、法律风险、空置等。"""
from japanai.agents.utils.agent_states import RealEstateAgentState


def create_conservative_debator(llm):
    def conservative_node(state: RealEstateAgentState) -> dict:
        rdeb = state["risk_debate_state"]
        history = rdeb.get("history", "")
        con_history = rdeb.get("conservative_history", "")
        cur_agg = rdeb.get("current_aggressive_response", "")
        cur_neu = rdeb.get("current_neutral_response", "")
        trader_plan = state["trader_investment_plan"]
        loc = state["location_report"]
        leg = state["legal_report"]
        pol = state.get("policy_report", "")
        tax = state["tax_report"]
        yld = state["yield_report"]

        prompt = f"""As the Conservative Risk Analyst, prioritize stability and risk mitigation for this real estate. Highlight liquidity, tax, legal, vacancy risks. Counter aggressive and neutral views. Trader plan: {trader_plan}
Reports: Location: {loc}; Legal: {leg}; Policy: {pol}; Tax: {tax}; Yield: {yld}
History: {history}. Last aggressive: {cur_agg}. Last neutral: {cur_neu}. If none, just present your view. Debate concisely, no special formatting."""

        response = llm.invoke(prompt)
        argument = f"Conservative Analyst: {response.content}"
        new_rdeb = {
            "history": history + "\n" + argument,
            "aggressive_history": rdeb.get("aggressive_history", ""),
            "conservative_history": con_history + "\n" + argument,
            "neutral_history": rdeb.get("neutral_history", ""),
            "latest_speaker": "Conservative",
            "current_aggressive_response": rdeb.get("current_aggressive_response", ""),
            "current_conservative_response": argument,
            "current_neutral_response": rdeb.get("current_neutral_response", ""),
            "judge_decision": rdeb.get("judge_decision", ""),
            "count": rdeb["count"] + 1,
        }
        return {"risk_debate_state": new_rdeb}

    return conservative_node
