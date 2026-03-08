"""
政策研究员：根据用户户籍/国籍，调用 get_policy_faq(household_region, target_country)，
产出「该国居民在目标国（如日本）购房政策与限制」报告，写入 state["policy_report"]。
"""
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from japanai.agents.utils.policy_tools import get_policy_faq


def create_policy_analyst(llm):
    """创建政策分析节点。"""

    def policy_analyst_node(state):
        property_of_interest = state["property_of_interest"]
        user_profile = state["user_profile"]
        household_region = state.get("household_region") or ""
        trade_date = state["trade_date"]
        tools = [get_policy_faq]

        system_message = """You are the Policy Analyst for cross-border real estate. Your conclusion is the **first gate**: if the buyer's country restricts or heavily burdens purchase in Japan, the deal may be non-viable regardless of other factors.

**Output format (strict):**
1. **结论（1–2 句）**：先明确「该国居民在日购房是否可行 / 有无重大限制 / 需进一步确认」，并给出关键依据（如资格、备案、汇兑）。
2. **依据**：用 get_policy_faq(household_region, target_country) 获取政策要点。说明：购房资格、贷款与汇兑、本国申报（如中国境外投资备案、美国 FBAR）、税务协定等。
3. **风险点**：政策变动、合规遗漏、资金出境限制等。
4. **简要表格**：用 Markdown 表总结（可行性、主要限制、建议确认项）。

不确定处必须写「需进一步确认」。target_country 为日本。"""

        prompt = ChatPromptTemplate.from_messages([
            ("system", "Current date: {trade_date}. Property: {property_of_interest}. User: {user_profile}. Household/Nationality: {household_region}. {system_message}"),
            MessagesPlaceholder(variable_name="messages"),
        ])
        prompt = prompt.partial(
            trade_date=trade_date,
            property_of_interest=property_of_interest,
            user_profile=user_profile,
            household_region=household_region or "未提供",
            system_message=system_message,
        )
        chain = prompt | llm.bind_tools(tools)
        result = chain.invoke(state["messages"])

        report = ""
        if not result.tool_calls:
            report = result.content or ""

        return {"messages": [result], "policy_report": report}

    return policy_analyst_node
