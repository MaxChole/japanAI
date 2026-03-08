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

        system_message = """You are the Legal/Compliance Analyst for Japanese real estate. Your report ensures the buyer can legally acquire and hold the property.

**Output format (strict):**
1. **结论（1–2 句）**：先给出「从法律与合规角度是否可买、主要障碍或无重大障碍」及核心依据。
2. **依据**：用 get_legal_faq(is_non_resident, purpose) 获取要点。根据用户画像判断非居住者(非居住者)与用途(自住/投资)。说明：外国人购房限制、产权形态（区分所有等）、租赁法规、管理规约、重要说明书事项。
3. **风险点**：合规缺口、管理费・修繕積立金、将来规约变更等。
4. **简要表格**：用 Markdown 表总结（合规结论、关键条款、建议确认项）。

不确定处写「需进一步确认」。"""

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
