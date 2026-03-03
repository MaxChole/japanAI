# Agent 节点：分析师、研究员、经理、交易员、风控辩论员、风控裁判
# 各 create_xxx 返回 (state) -> dict 的节点函数，仅更新需要写入的 state 字段

from .utils.agent_states import (
    RealEstateAgentState,
    InvestDebateState,
    RiskDebateState,
)
from .analysts.location_analyst import create_location_analyst
from .analysts.legal_analyst import create_legal_analyst
from .analysts.policy_analyst import create_policy_analyst
from .analysts.tax_analyst import create_tax_analyst
from .analysts.yield_analyst import create_yield_analyst
from .researchers.bull_researcher import create_bull_researcher
from .researchers.bear_researcher import create_bear_researcher
from .managers.research_manager import create_research_manager
from .managers.risk_manager import create_risk_manager
from .trader.trader import create_trader
from .risk_mgmt.aggressive_debator import create_aggressive_debator
from .risk_mgmt.conservative_debator import create_conservative_debator
from .risk_mgmt.neutral_debator import create_neutral_debator

__all__ = [
    "RealEstateAgentState",
    "InvestDebateState",
    "RiskDebateState",
    "create_location_analyst",
    "create_legal_analyst",
    "create_policy_analyst",
    "create_tax_analyst",
    "create_yield_analyst",
    "create_bull_researcher",
    "create_bear_researcher",
    "create_research_manager",
    "create_risk_manager",
    "create_trader",
    "create_aggressive_debator",
    "create_conservative_debator",
    "create_neutral_debator",
]
