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

        prompt = f"""As the Research Manager, synthesize the analyst reports and debate into a single recommendation. Apply this **decision order** (do not ignore):

1. **Policy first (一票否决)**：若政策报告结论为「不可行」或「存在重大限制需确认」，倾向 Avoid 或 Hold，并在理由中明确引用政策结论。
2. **Location second**：地段结论决定标的档次与长期价值；若地段为「谨慎/不建议」，需在理由中体现并相应下调倾向。
3. **Legal / Yield / Tax**：合规、收益与税负作为支撑或修正，不单独否决除非存在明确障碍。

Output: (1) 明确 Recommendation：Buy / Avoid (Sell) / Hold，并一句话说明理由；(2) 引用哪些分析师的结论支撑（尤其是 Policy、Location）；(3) 给 Trader 的简短投资计划：Recommendation, Rationale, Strategic Actions。用 past reflections 避免重复错误。

Past reflections: {past_memory_str}

Analyst reports (Policy / Location / Legal / Tax / Yield) and debate context:
{curr_situation}

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
