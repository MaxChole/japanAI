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

        system_message = """You are the Tax Analyst for Japanese real estate. Your report supports investment feasibility (holding cost and exit tax), not the sole deal-breaker.

**Output format (strict):**
1. **结论（1–2 句）**：先给出「税负水平可接受/需注意/建议进一步规划」及主要税种影响（持有成本 vs 出售时税负）。
2. **依据**：用 get_tax_rules(purpose, holding_years) 获取规则。根据用户画像判断用途(自住/投资)与预计持有期。必须涉及：固定資産税・都市計画税、租金所得税、非居住者源泉徴収(20.42%)、折旧(耐用年数 22 年/47 年)、出售时所得税・住民税(短期/长期)。
3. **风险点**：税率或税务协定变动、申报义务遗漏等。
4. **简要表格**：用 Markdown 表总结（持有期税负、出售时税负、非居住者要点）。

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

        return {"messages": [result], "tax_report": report}

    return tax_analyst_node
