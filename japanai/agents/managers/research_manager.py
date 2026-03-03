"""
研究经理（投资辩论裁判）：在多空辩论结束后，总结双方论点，结合记忆做出
Buy/Hold/Avoid 建议，并生成详细投资计划摘要（investment_plan）供 Trader 使用。
"""
from japanai.agents.utils.agent_states import RealEstateAgentState


def create_research_manager(llm, memory):
    """创建研究经理节点：消费 investment_debate_state 与四份报告，输出 investment_plan。"""

    def research_manager_node(state: RealEstateAgentState) -> dict:
        ideb = state["investment_debate_state"]
        history = ideb.get("history", "")
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

        prompt = f"""As the Research Manager and debate facilitator, evaluate this round of debate and make a clear decision: align with the bear, the bull, or choose Hold only if strongly justified. Summarize the strongest points from both sides. Your recommendation must be one of: Buy, Sell (or Avoid), or Hold—clear and actionable. Then develop a short investment plan for the trader: Recommendation, Rationale, Strategic Actions. Use past reflections to avoid repeating mistakes.

Past reflections: {past_memory_str}

Debate history:
{history}"""

        response = llm.invoke(prompt)
        new_debate = {
            **ideb,
            "judge_decision": response.content,
            "current_response": response.content,
        }
        return {
            "investment_debate_state": new_debate,
            "investment_plan": response.content,
        }

    return research_manager_node
