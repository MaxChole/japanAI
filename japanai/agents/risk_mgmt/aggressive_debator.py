"""激进风控辩论员：强调高回报、杠杆与长期持有收益。"""
from japanai.agents.utils.agent_states import RealEstateAgentState


def create_aggressive_debator(llm):
    def aggressive_node(state: RealEstateAgentState) -> dict:
        rdeb = state["risk_debate_state"]
        history = rdeb.get("history", "")
        agg_history = rdeb.get("aggressive_history", "")
        cur_con = rdeb.get("current_conservative_response", "")
        cur_neu = rdeb.get("current_neutral_response", "")
        trader_plan = state["trader_investment_plan"]
        loc = state["location_report"]
        leg = state["legal_report"]
        pol = state.get("policy_report", "")
        tax = state["tax_report"]
        yld = state["yield_report"]

        prompt = f"""As the Aggressive Risk Analyst, champion high-reward opportunities for this real estate. Emphasize upside, growth, and benefits. Counter the conservative and neutral views. Trader plan: {trader_plan}
Reports: Location: {loc}; Legal: {leg}; Policy: {pol}; Tax: {tax}; Yield: {yld}
History: {history}. Last conservative: {cur_con}. Last neutral: {cur_neu}. If none, just present your view. Debate concisely, no special formatting."""

        response = llm.invoke(prompt)
        argument = f"Aggressive Analyst: {response.content}"
        new_rdeb = {
            "history": history + "\n" + argument,
            "aggressive_history": agg_history + "\n" + argument,
            "conservative_history": rdeb.get("conservative_history", ""),
            "neutral_history": rdeb.get("neutral_history", ""),
            "latest_speaker": "Aggressive",
            "current_aggressive_response": argument,
            "current_conservative_response": rdeb.get("current_conservative_response", ""),
            "current_neutral_response": rdeb.get("current_neutral_response", ""),
            "judge_decision": rdeb.get("judge_decision", ""),
            "count": rdeb["count"] + 1,
        }
        return {"risk_debate_state": new_rdeb}

    return aggressive_node
