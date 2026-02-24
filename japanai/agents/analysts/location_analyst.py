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

        system_message = """You are the Location Analyst for Japanese real estate. Your task is to analyze the area/location of the property of interest. Use the tool get_location_data(region, purpose) to retrieve area data (e.g. trend, transport, population). Infer region and purpose (自住 or 投资) from the property description and user profile. Write a concise report covering: location potential, transport, population, planning, and risk points. If information is uncertain, say so. End with a Markdown table summarizing key points."""

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
