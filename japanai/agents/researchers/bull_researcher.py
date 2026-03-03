"""
Bull 研究员：在多空辩论中代表看多一方，强调该房产的增值潜力、租金稳定性、
政策友好、稀缺性等，反驳 Bear 的论点，并利用记忆中的相似情境反思。
"""
from japanai.agents.utils.agent_states import RealEstateAgentState


def create_bull_researcher(llm, memory):
    """创建 Bull 辩论节点：读四份报告与 investment_debate_state，输出己方论点并更新辩论状态。"""

    def bull_node(state: RealEstateAgentState) -> dict:
        ideb = state["investment_debate_state"]
        history = ideb.get("history", "")
        bull_history = ideb.get("bull_history", "")
        current_response = ideb.get("current_response", "")  # 上一轮 Bear 的发言
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

        prompt = f"""You are the Bull Analyst advocating for investing in this Japanese real estate. Build an evidence-based case emphasizing: growth potential, rental stability, policy friendliness, scarcity. Use the reports below and counter the bear's arguments. Address past lessons if provided.

Location report: {loc}
Legal report: {leg}
Policy report: {pol}
Tax report: {tax}
Yield report: {yld}
Debate history: {history}
Last bear argument: {current_response}
Past reflections: {past_memory_str}

Deliver a concise bull argument; engage with the bear's points. Do not use special formatting."""

        response = llm.invoke(prompt)
        argument = f"Bull Analyst: {response.content}"

        new_debate = {
            "history": history + "\n" + argument,
            "bull_history": bull_history + "\n" + argument,
            "bear_history": ideb.get("bear_history", ""),
            "current_response": argument,
            "judge_decision": ideb.get("judge_decision", ""),
            "count": ideb["count"] + 1,
        }
        return {"investment_debate_state": new_debate}

    return bull_node
