"""
Bear 研究员：在多空辩论中代表看空一方，强调泡沫风险、空置、利率、
法律/税务负担、流动性等，反驳 Bull 的论点，并利用记忆反思。
"""
from japanai.agents.utils.agent_states import RealEstateAgentState


def create_bear_researcher(llm, memory):
    """创建 Bear 辩论节点：读四份报告与对方最新发言，输出己方论点并更新辩论状态。"""

    def bear_node(state: RealEstateAgentState) -> dict:
        ideb = state["investment_debate_state"]
        history = ideb.get("history", "")
        bear_history = ideb.get("bear_history", "")
        current_response = ideb.get("current_response", "")
        loc = state["location_report"]
        leg = state["legal_report"]
        tax = state["tax_report"]
        yld = state["yield_report"]

        curr_situation = f"{loc}\n\n{leg}\n\n{tax}\n\n{yld}"
        past_memories = memory.get_memories(curr_situation, n_matches=2)
        past_memory_str = "\n\n".join(
            rec["recommendation"] for rec in past_memories
        ) if past_memories else ""

        prompt = f"""You are the Bear Analyst arguing against investing in this Japanese real estate. Emphasize: bubble risk, vacancy, interest rate, legal/tax burden, liquidity. Use the reports below and counter the bull's arguments. Address past lessons if provided.

Location report: {loc}
Legal report: {leg}
Tax report: {tax}
Yield report: {yld}
Debate history: {history}
Last bull argument: {current_response}
Past reflections: {past_memory_str}

Deliver a concise bear argument; engage with the bull's points. Do not use special formatting."""

        response = llm.invoke(prompt)
        argument = f"Bear Analyst: {response.content}"

        new_debate = {
            "history": history + "\n" + argument,
            "bear_history": bear_history + "\n" + argument,
            "bull_history": ideb.get("bull_history", ""),
            "current_response": argument,
            "judge_decision": ideb.get("judge_decision", ""),
            "count": ideb["count"] + 1,
        }
        return {"investment_debate_state": new_debate}

    return bear_node
