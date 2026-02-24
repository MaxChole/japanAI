"""
收益/现金流分析师：调用 get_yield_inputs(rent_monthly, price, ...)，
产出表面/净回报率、空置与费用假设等报告，写入 state["yield_report"]。
"""
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from japanai.agents.utils.yield_tools import get_yield_inputs


def create_yield_analyst(llm):
    """创建收益分析节点。"""

    def yield_analyst_node(state):
        property_of_interest = state["property_of_interest"]
        user_profile = state["user_profile"]
        trade_date = state["trade_date"]
        tools = [get_yield_inputs]

        system_message = """You are the Yield/Cashflow Analyst for Japanese real estate. Use the tool get_yield_inputs(rent_monthly, price, management_fee_ratio, vacancy_ratio) to get yield metrics. Infer or assume reasonable rent/price and ratios from property and user profile if not clearly given. Report on: gross/net yield, vacancy and cost assumptions, simple sensitivity. End with a Markdown table."""

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

        return {"messages": [result], "yield_report": report}

    return yield_analyst_node
