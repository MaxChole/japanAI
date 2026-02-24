"""
风控裁判：在激进/保守/中性三方辩论后，评估辩论内容与交易员计划，
结合记忆输出最终决策（final_decision：BUY/HOLD/AVOID）及理由。
"""
from japanai.agents.utils.agent_states import RealEstateAgentState


def create_risk_manager(llm, memory):
    """创建风控裁判节点：消费 risk_debate_state、trader_investment_plan 与报告，输出 final_decision。"""

    def risk_manager_node(state: RealEstateAgentState) -> dict:
        rdeb = state["risk_debate_state"]
        history = rdeb.get("history", "")
        trader_plan = state["trader_investment_plan"]
        loc = state["location_report"]
        leg = state["legal_report"]
        tax = state["tax_report"]
        yld = state["yield_report"]

        curr_situation = f"{loc}\n\n{leg}\n\n{tax}\n\n{yld}"
        past_memories = memory.get_memories(curr_situation, n_matches=2)
        past_memory_str = "\n\n".join(
            rec["recommendation"] for rec in past_memories
        ) if past_memories else ""

        prompt = f"""As the Risk Management Judge, evaluate the debate between the Aggressive, Neutral, and Conservative analysts and decide the best course of action. Your decision must be one of: BUY, HOLD, or AVOID. Choose HOLD only if strongly justified. Summarize key arguments, provide rationale, and refine the trader's plan based on the debate. Use past lessons to improve the decision.

Past reflections: {past_memory_str}

Trader plan: {trader_plan}

Analysts debate history:
{history}

Deliver a clear, actionable recommendation (BUY/HOLD/AVOID) with short reasoning."""

        response = llm.invoke(prompt)
        new_rdeb = {
            **rdeb,
            "judge_decision": response.content,
            "latest_speaker": "Judge",
        }
        return {
            "risk_debate_state": new_rdeb,
            "final_decision": response.content,
        }

    return risk_manager_node
