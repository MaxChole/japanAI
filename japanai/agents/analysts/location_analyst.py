"""
区域/地段分析师：根据标的与用户画像调用 get_location_data 等工具，
产出地段潜力、交通、人口、规划、风险点等报告，写入 state["location_report"]。
"""
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from japanai.agents.utils.location_tools import get_location_data


def create_location_analyst(llm):
    """创建区域分析节点：可调用 get_location_data(region, purpose)，报告末尾建议附 Markdown 表格。"""

    def location_analyst_node(state):
        property_of_interest = state["property_of_interest"]
        user_profile = state["user_profile"]
        trade_date = state["trade_date"]
        tools = [get_location_data]

        system_message = """You are the Location Analyst for Japanese real estate. Your report drives the "where to buy" decision and long-term value.

**Output format (strict):**
1. **结论（1–2 句）**：先给出明确结论，如「该地段值得/谨慎/不建议投资」及核心理由。
2. **依据**：用 get_location_data(region, purpose) 获取数据。若有成交数据（Total transaction value, Area, Land price per m2 等），必须引用具体数值；若无则说明数据局限。涵盖：交通（駅距離・路線）、人口・再开发、用途地域、地价动向。
3. **风险点**：流动性、空置、灾害（如液状化）等。
4. **简要表格**：用 Markdown 表总结要点（地段等级、交通、主要风险）。

使用日本常用表述：駅徒歩、用途地域、公示地价、再開発等。"""

        prompt = ChatPromptTemplate.from_messages([
            ("system", "You are a helpful AI assistant. Use the provided tools to answer. Current date: {trade_date}. Property: {property_of_interest}. User profile: {user_profile}. {system_message}"),
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

        # 仅当 LLM 不再发起工具调用时（即已生成最终报告）才写入 report，否则由下一轮带着 tool 结果再跑
        report = ""
        if not result.tool_calls:
            report = result.content or ""

        return {"messages": [result], "location_report": report}

    return location_analyst_node
