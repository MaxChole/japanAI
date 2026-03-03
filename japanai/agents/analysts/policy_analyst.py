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

        system_message = """You are the Policy Analyst for cross-border real estate. Use the tool get_policy_faq(household_region, target_country) to get policy points. Infer household_region (户籍/国籍/常居地) from user profile if not explicitly given; target_country is 日本. Report on: purchase eligibility, lending rules, FX/remittance, home-country reporting (e.g. China 境外投资备案, US FBAR). If uncertain, state "需进一步确认". End with a short Markdown table."""

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
