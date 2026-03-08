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
        pol = state.get("policy_report", "")
        tax = state["tax_report"]
        yld = state["yield_report"]

        curr_situation = f"{loc}\n\n{leg}\n\n{pol}\n\n{tax}\n\n{yld}"
        past_memories = memory.get_memories(curr_situation, n_matches=2)
        past_memory_str = "\n\n".join(
            rec["recommendation"] for rec in past_memories
        ) if past_memories else ""

        prompt = f"""As the Risk Management Judge, issue the final BUY / HOLD / AVOID. Apply this **decision order** (mandatory):

1. **Policy (一票否决)**：若政策报告结论为不可行或存在重大限制未解决，必须倾向 AVOID 或 HOLD，并在最终理由中明确写出「政策面：…」。
2. **Location**：地段结论为「不建议/谨慎」时，在理由中体现并相应下调信号；地段为「值得」时可作为 BUY 的重要依据。
3. **Legal / Yield / Tax**：作为补充依据，若有明确风险（如合规缺口、净利回り过低）需在理由中写明。

Output: (1) 最终信号：BUY / HOLD / AVOID；(2) 2–4 句理由，必须引用政策与地段结论（例如「政策面：…；地段：…」）；(3) 对 Trader 计划的修正或确认。Use past lessons to avoid repeated mistakes.

Past reflections: {past_memory_str}

Analyst reports (Policy / Location / Legal / Tax / Yield):
{curr_situation}

Trader plan: {trader_plan}

Risk debate history:
{history}

Deliver a clear, actionable final recommendation (BUY/HOLD/AVOID) with short, citation-based reasoning."""

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
