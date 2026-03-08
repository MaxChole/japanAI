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

        system_message = """You are the Yield/Cashflow Analyst for Japanese real estate. Your report answers "does the investment make financial sense" (cash flow and yield).

**Output format (strict):**
1. **结论（1–2 句）**：先给出「表面/净回报率是否达标、现金流是否健康、建议/谨慎/不建议从收益角度入手」及关键数字。
2. **依据**：用 get_yield_inputs(rent_monthly, price, management_fee_ratio, vacancy_ratio) 计算。未给出时从标的与用户画像做合理假设并注明。说明：表面利回り・净利回り、空室率与费用假设（管理费・修繕積立金・固都税等）、简单敏感性（租金降 10% 等）。
3. **风险点**：空室、租金下行、费用上涨、汇率（若外币投资）等。
4. **简要表格**：用 Markdown 表总结（表面/净利回り、假设条件、敏感性结论）。

使用日本常用表述：表面利回り、净利回り、修繕積立金等。"""

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
