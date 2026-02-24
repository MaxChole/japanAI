"""
法律/合规分析师：调用 get_legal_faq(is_non_resident, purpose)，
产出外国人购房、产权、租赁法规、管理规约等报告，写入 state["legal_report"]。
"""
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from japanai.agents.utils.legal_tools import get_legal_faq


def create_legal_analyst(llm):
    """创建法律分析节点。"""

    def legal_analyst_node(state):
        property_of_interest = state["property_of_interest"]
        user_profile = state["user_profile"]
        trade_date = state["trade_date"]
        tools = [get_legal_faq]

        system_message = """You are the Legal/Compliance Analyst for Japanese real estate. Use the tool get_legal_faq(is_non_resident, purpose) to get regulatory points. Infer from user profile whether the buyer is non-resident (非居住者) and purpose (自住 or 投资). Report on: foreign buyer rules, ownership types, rental law, management rules. If uncertain, state "需进一步确认". End with a short Markdown table."""

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

        return {"messages": [result], "legal_report": report}

    return legal_analyst_node
