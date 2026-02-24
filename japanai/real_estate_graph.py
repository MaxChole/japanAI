"""
地产投资建议图主入口：初始化 LLM、记忆、工具节点、图编排，
提供 propagate(property_of_interest, user_profile, trade_date) 与 process_signal(final_decision)。

流程简述：
  1. 分析师链（Location → Legal → Tax → Yield）各调用 dataflows 工具产报告；
  2. Bull/Bear 多轮辩论后由 Research Manager 产出投资计划；
  3. Trader 根据计划产出带 FINAL RECOMMENDATION 的可执行方案；
  4. 风控三方辩论后由 Risk Judge 产出 final_decision（BUY/HOLD/AVOID）。
"""
from datetime import date
from typing import Any, Dict, List, Optional, Tuple

from langgraph.prebuilt import ToolNode

from japanai.llm_clients import create_llm_client
from japanai.agents.utils.agent_states import RealEstateAgentState
from japanai.agents.utils.memory import RealEstateSituationMemory
from japanai.agents.utils.location_tools import get_location_data
from japanai.agents.utils.legal_tools import get_legal_faq
from japanai.agents.utils.tax_tools import get_tax_rules
from japanai.agents.utils.yield_tools import get_yield_inputs
from japanai.dataflows.config import set_config
from japanai.graph.conditional_logic import ConditionalLogic
from japanai.graph.setup import GraphSetup
from japanai.graph.propagation import Propagator
from japanai.graph.signal_processing import SignalProcessor

from .default_config import DEFAULT_CONFIG


class RealEstateGraph:
    """日本地产投资建议多 Agent 图：分析师链 → 多空辩论 → 研究经理 → 交易员 → 风控辩论 → 风控裁判。"""

    def __init__(
        self,
        selected_analysts: Optional[List[str]] = None,
        debug: bool = False,
        config: Optional[Dict[str, Any]] = None,
        callbacks: Optional[List] = None,
    ):
        """
        Args:
            selected_analysts: 参与的分析师类型，默认 ["location", "legal", "tax", "yield"]
            debug: 是否以 stream 方式打印中间结果
            config: 配置字典，缺省用 DEFAULT_CONFIG
            callbacks: 可选回调列表
        """
        self.debug = debug
        self.config = config or DEFAULT_CONFIG
        self.callbacks = callbacks or []
        set_config(self.config)

        deep_client = create_llm_client(
            provider=self.config["llm_provider"],
            model=self.config["deep_think_llm"],
            base_url=self.config.get("backend_url"),
            **self._llm_kwargs(),
        )
        quick_client = create_llm_client(
            provider=self.config["llm_provider"],
            model=self.config["quick_think_llm"],
            base_url=self.config.get("backend_url"),
            **self._llm_kwargs(),
        )
        self.deep_llm = deep_client.get_llm()
        self.quick_llm = quick_client.get_llm()

        # BM25 记忆：各角色检索「与当前情境相似」的历史建议，减少重复错误
        self.bull_memory = RealEstateSituationMemory("bull_memory", self.config)
        self.bear_memory = RealEstateSituationMemory("bear_memory", self.config)
        self.trader_memory = RealEstateSituationMemory("trader_memory", self.config)
        self.invest_judge_memory = RealEstateSituationMemory(
            "invest_judge_memory", self.config
        )
        self.risk_manager_memory = RealEstateSituationMemory(
            "risk_manager_memory", self.config
        )

        self.tool_nodes = {
            "location": ToolNode([get_location_data]),
            "legal": ToolNode([get_legal_faq]),
            "tax": ToolNode([get_tax_rules]),
            "yield": ToolNode([get_yield_inputs]),
        }

        self.conditional_logic = ConditionalLogic(
            max_debate_rounds=1,
            max_risk_discuss_rounds=1,
        )
        self.graph_setup = GraphSetup(
            self.quick_llm,
            self.deep_llm,
            self.tool_nodes,
            self.bull_memory,
            self.bear_memory,
            self.trader_memory,
            self.invest_judge_memory,
            self.risk_manager_memory,
            self.conditional_logic,
        )
        self.propagator = Propagator()
        self.signal_processor = SignalProcessor(self.quick_llm)

        self.graph = self.graph_setup.setup_graph(
            selected_analysts=selected_analysts or ["location", "legal", "tax", "yield"]
        )
        self.curr_state: Optional[Dict[str, Any]] = None

    def _llm_kwargs(self) -> Dict[str, Any]:
        out = {}
        if self.callbacks:
            out["callbacks"] = self.callbacks
        return out

    def propagate(
        self,
        property_of_interest: str,
        user_profile: str,
        trade_date: Optional[str] = None,
    ) -> Tuple[Dict[str, Any], str]:
        """
        运行图并返回最终 state 与抽取的决策（BUY/HOLD/AVOID）。

        Args:
            property_of_interest: 地产标的描述
            user_profile: 用户画像（预算、用途、是否非居住者等）
            trade_date: 分析基准日，默认今天

        Returns:
            (final_state, signal) 其中 signal 为 "BUY" | "HOLD" | "AVOID"
        """
        if trade_date is None:
            trade_date = str(date.today())
        init_state = self.propagator.create_initial_state(
            property_of_interest, user_profile, trade_date
        )
        args = self.propagator.get_graph_args(self.callbacks)

        if self.debug:
            trace = []
            for chunk in self.graph.stream(init_state, **args):
                trace.append(chunk)
            final_state = trace[-1] if trace else init_state
        else:
            final_state = self.graph.invoke(init_state, **args)

        self.curr_state = final_state
        signal = self.process_signal(final_state.get("final_decision") or "")
        return final_state, signal

    def process_signal(self, full_signal: str) -> str:
        """从完整 final_decision 文本中抽取 BUY/HOLD/AVOID。"""
        return self.signal_processor.process_signal(full_signal)
