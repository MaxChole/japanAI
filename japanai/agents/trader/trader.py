"""
交易员节点：根据 research_manager 产出的投资计划与四份报告，结合历史记忆，
给出带 FINAL RECOMMENDATION: BUY/HOLD/AVOID 的可执行计划，写入 trader_investment_plan 供风控辩论使用。
"""
import functools
from japanai.agents.utils.agent_states import RealEstateAgentState


def create_trader(llm, memory):
    """创建交易员节点；输出 trader_investment_plan、messages。"""

    def trader_node(state: RealEstateAgentState, name: str):
        property_of_interest = state["property_of_interest"]
        investment_plan = state["investment_plan"]
        loc = state["location_report"]
        leg = state["legal_report"]
        tax = state["tax_report"]
        yld = state["yield_report"]

        curr_situation = f"{loc}\n\n{leg}\n\n{tax}\n\n{yld}"
        past_memories = memory.get_memories(curr_situation, n_matches=2)
        past_memory_str = "\n\n".join(
            rec["recommendation"] for rec in past_memories
        ) if past_memories else "No past memories."

        context = {
            "role": "user",
            "content": f"Property: {property_of_interest}. Investment plan from Research Manager: {investment_plan}. Use this and the reports to form an actionable recommendation.",
        }
        messages = [
            {
                "role": "system",
                "content": f"You are a real estate advisor. Provide a clear recommendation and end with exactly: FINAL RECOMMENDATION: **BUY** or FINAL RECOMMENDATION: **HOLD** or FINAL RECOMMENDATION: **AVOID**. Use past lessons: {past_memory_str}",
            },
            context,
        ]
        result = llm.invoke(messages)
        return {
            "messages": [result],
            "trader_investment_plan": result.content,
        }

    return functools.partial(trader_node, name="Trader")
