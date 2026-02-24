"""
图构建：使用 StateGraph(RealEstateAgentState) 添加所有节点与边，
分析师链 → 多空辩论 → Research Manager → Trader → 风控辩论 → Risk Judge → END。
"""
from typing import Dict
from langgraph.graph import END, StateGraph, START
from langgraph.prebuilt import ToolNode

from japanai.agents.utils.agent_states import RealEstateAgentState
from japanai.agents.utils.agent_utils import create_msg_delete
from japanai.agents.utils.location_tools import get_location_data
from japanai.agents.utils.legal_tools import get_legal_faq
from japanai.agents.utils.tax_tools import get_tax_rules
from japanai.agents.utils.yield_tools import get_yield_inputs
from japanai.agents.analysts.location_analyst import create_location_analyst
from japanai.agents.analysts.legal_analyst import create_legal_analyst
from japanai.agents.analysts.tax_analyst import create_tax_analyst
from japanai.agents.analysts.yield_analyst import create_yield_analyst
from japanai.agents.researchers.bull_researcher import create_bull_researcher
from japanai.agents.researchers.bear_researcher import create_bear_researcher
from japanai.agents.managers.research_manager import create_research_manager
from japanai.agents.managers.risk_manager import create_risk_manager
from japanai.agents.trader.trader import create_trader
from japanai.agents.risk_mgmt.aggressive_debator import create_aggressive_debator
from japanai.agents.risk_mgmt.conservative_debator import create_conservative_debator
from japanai.agents.risk_mgmt.neutral_debator import create_neutral_debator

from .conditional_logic import ConditionalLogic


class GraphSetup:
    """组装并编译地产投资建议图。"""

    def __init__(
        self,
        quick_llm,
        deep_llm,
        tool_nodes: Dict[str, ToolNode],
        bull_memory,
        bear_memory,
        trader_memory,
        invest_judge_memory,
        risk_manager_memory,
        conditional_logic: ConditionalLogic,
    ):
        self.quick_llm = quick_llm
        self.deep_llm = deep_llm
        self.tool_nodes = tool_nodes
        self.bull_memory = bull_memory
        self.bear_memory = bear_memory
        self.trader_memory = trader_memory
        self.invest_judge_memory = invest_judge_memory
        self.risk_manager_memory = risk_manager_memory
        self.conditional_logic = conditional_logic

    def setup_graph(
        self,
        selected_analysts=None,
    ):
        """构建图。selected_analysts 默认即四类全选：location, legal, tax, yield。"""
        if selected_analysts is None:
            selected_analysts = ["location", "legal", "tax", "yield"]
        if not selected_analysts:
            raise ValueError("At least one analyst must be selected.")

        analyst_nodes = {}
        delete_nodes = {}

        if "location" in selected_analysts:
            analyst_nodes["location"] = create_location_analyst(self.quick_llm)
            delete_nodes["location"] = create_msg_delete()
        if "legal" in selected_analysts:
            analyst_nodes["legal"] = create_legal_analyst(self.quick_llm)
            delete_nodes["legal"] = create_msg_delete()
        if "tax" in selected_analysts:
            analyst_nodes["tax"] = create_tax_analyst(self.quick_llm)
            delete_nodes["tax"] = create_msg_delete()
        if "yield" in selected_analysts:
            analyst_nodes["yield"] = create_yield_analyst(self.quick_llm)
            delete_nodes["yield"] = create_msg_delete()

        bull_node = create_bull_researcher(self.quick_llm, self.bull_memory)
        bear_node = create_bear_researcher(self.quick_llm, self.bear_memory)
        research_manager_node = create_research_manager(
            self.deep_llm, self.invest_judge_memory
        )
        trader_node = create_trader(self.quick_llm, self.trader_memory)
        aggressive_node = create_aggressive_debator(self.quick_llm)
        conservative_node = create_conservative_debator(self.quick_llm)
        neutral_node = create_neutral_debator(self.quick_llm)
        risk_manager_node = create_risk_manager(
            self.deep_llm, self.risk_manager_memory
        )

        workflow = StateGraph(RealEstateAgentState)

        for analyst_type, node in analyst_nodes.items():
            cap = analyst_type.capitalize()
            workflow.add_node(f"{cap} Analyst", node)
            workflow.add_node(f"Msg Clear {cap}", delete_nodes[analyst_type])
            workflow.add_node(f"tools_{analyst_type}", self.tool_nodes[analyst_type])

        workflow.add_node("Bull Researcher", bull_node)
        workflow.add_node("Bear Researcher", bear_node)
        workflow.add_node("Research Manager", research_manager_node)
        workflow.add_node("Trader", trader_node)
        workflow.add_node("Aggressive Analyst", aggressive_node)
        workflow.add_node("Conservative Analyst", conservative_node)
        workflow.add_node("Neutral Analyst", neutral_node)
        workflow.add_node("Risk Judge", risk_manager_node)

        first = selected_analysts[0]
        workflow.add_edge(START, f"{first.capitalize()} Analyst")

        # 分析师链：每个分析师后根据是否有 tool_calls 决定进 tools 或 Msg Clear，再进入下一分析师或 Bull
        for i, analyst_type in enumerate(selected_analysts):
            cap = analyst_type.capitalize()
            current_analyst = f"{cap} Analyst"
            current_tools = f"tools_{analyst_type}"
            current_clear = f"Msg Clear {cap}"
            workflow.add_conditional_edges(
                current_analyst,
                getattr(self.conditional_logic, f"should_continue_{analyst_type}"),
                [current_tools, current_clear],
            )
            workflow.add_edge(current_tools, current_analyst)
            if i < len(selected_analysts) - 1:
                next_cap = selected_analysts[i + 1].capitalize()
                workflow.add_edge(current_clear, f"{next_cap} Analyst")
            else:
                workflow.add_edge(current_clear, "Bull Researcher")

        workflow.add_conditional_edges(
            "Bull Researcher",
            self.conditional_logic.should_continue_debate,
            {"Bear Researcher": "Bear Researcher", "Research Manager": "Research Manager"},
        )
        workflow.add_conditional_edges(
            "Bear Researcher",
            self.conditional_logic.should_continue_debate,
            {"Bull Researcher": "Bull Researcher", "Research Manager": "Research Manager"},
        )
        workflow.add_edge("Research Manager", "Trader")
        workflow.add_edge("Trader", "Aggressive Analyst")
        workflow.add_conditional_edges(
            "Aggressive Analyst",
            self.conditional_logic.should_continue_risk_analysis,
            {"Conservative Analyst": "Conservative Analyst", "Risk Judge": "Risk Judge"},
        )
        workflow.add_conditional_edges(
            "Conservative Analyst",
            self.conditional_logic.should_continue_risk_analysis,
            {"Neutral Analyst": "Neutral Analyst", "Risk Judge": "Risk Judge"},
        )
        workflow.add_conditional_edges(
            "Neutral Analyst",
            self.conditional_logic.should_continue_risk_analysis,
            {"Aggressive Analyst": "Aggressive Analyst", "Risk Judge": "Risk Judge"},
        )
        workflow.add_edge("Risk Judge", END)

        return workflow.compile()
