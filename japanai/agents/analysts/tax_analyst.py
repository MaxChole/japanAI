"""
税务分析师：调用 get_tax_rules(purpose, holding_years)，
产出固定资产税、所得税、源泉税、折旧等报告，写入 state["tax_report"]。
"""
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from japanai.agents.utils.tax_tools import get_tax_rules


def create_tax_analyst(llm):
    """创建税务分析节点。"""

    def tax_analyst_node(state):
        property_of_interest = state["property_of_interest"]
        user_profile = state["user_profile"]
        trade_date = state["trade_date"]
        tools = [get_tax_rules]

        system_message = """You are the Tax Analyst for Japanese real estate. Use the tool get_tax_rules(purpose, holding_years) to get tax rules. Infer purpose (自住 or 投资) and expected holding period from user profile. Report on: fixed asset tax, income tax on rent, withholding for non-residents, depreciation (e.g. 22/47 years). If uncertain, state "需进一步确认". End with a short Markdown table."""

        prompt = ChatPromptTemplate.from_messages([
            ("system", "Current date: {trade_date}. Property: {property_of_interest}. User: {user_profile}. {system_message}"),
            MessagesPlaceholder(variable_name="messages"),
        ])
        prompt = prompt.partial(
            trade_date=trade_date,
            property_of_interest=property_of_interest,
            user_profile=user_profile,
            system_message=system_message,
        )
        chain = prompt | llm.bind_tools(tools)
        result = chain.invoke(state["messages"])

        report = ""
        if not result.tool_calls:
            report = result.content or ""

        return {"messages": [result], "tax_report": report}

    return tax_analyst_node
