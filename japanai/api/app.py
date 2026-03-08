"""
FastAPI 应用：提供 POST /advise 接口，入参为标的、用户画像、可选基准日、
可选 LLM 配置（provider/model/api_key/base_url）与图参数，返回最终决策及各报告。
"""
from datetime import date
from typing import Any, Dict, List, Optional

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from japanai.real_estate_graph import RealEstateGraph
from japanai.default_config import DEFAULT_CONFIG
from japanai.utils.step_logger import log_step
from japanai.utils.token_usage_callback import TokenUsageCallback

app = FastAPI(
    title="JapanAI 地产投资建议",
    description="多角色 Agent 产出 BUY/HOLD/AVOID 及可执行建议；支持前端传入模型与 Token。",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 默认图实例（无自定义配置时复用）
_graph: Optional[RealEstateGraph] = None


def _build_config(llm_config: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """合并默认配置与请求中的 LLM 配置。"""
    config = dict(DEFAULT_CONFIG)
    if llm_config:
        for k, v in llm_config.items():
            if v is not None:
                config[k] = v
    return config


def get_or_create_graph(
    llm_config: Optional[Dict[str, Any]] = None,
    selected_analysts: Optional[List[str]] = None,
    use_risk_debate: Optional[bool] = None,
    debug: bool = False,
    max_debate_rounds: Optional[int] = None,
    max_risk_discuss_rounds: Optional[int] = None,
) -> RealEstateGraph:
    """有自定义配置时每次新建图，否则复用全局图。"""
    global _graph
    if (
        llm_config
        or selected_analysts is not None
        or use_risk_debate is not None
        or max_debate_rounds is not None
        or max_risk_discuss_rounds is not None
    ):
        config = _build_config(llm_config)
        if max_debate_rounds is not None:
            config["max_debate_rounds"] = max_debate_rounds
        if max_risk_discuss_rounds is not None:
            config["max_risk_discuss_rounds"] = max_risk_discuss_rounds
        if use_risk_debate is not None:
            config["use_risk_debate"] = use_risk_debate
        return RealEstateGraph(
            config=config,
            selected_analysts=selected_analysts or ["location", "legal", "policy", "tax", "yield"],
            use_risk_debate=config.get("use_risk_debate"),
            debug=debug,
        )
    if _graph is None:
        _graph = RealEstateGraph()
    return _graph


# ---------- 请求/响应模型 ----------


class LLMConfig(BaseModel):
    """前端可传入的 LLM 配置（模型与 Token）。"""
    provider: Optional[str] = Field(None, description="openai | openrouter | ollama | 或兼容 OpenAI API 的厂商如 minimax")
    deep_think_llm: Optional[str] = Field(None, description="深思模型名，如 gpt-4o-mini、minimax 模型名")
    quick_think_llm: Optional[str] = Field(None, description="快思模型名")
    api_key: Optional[str] = Field(None, description="API Key / Token")
    backend_url: Optional[str] = Field(None, description="自定义 API 基地址，如 MiniMax、OpenRouter 等")


class AdviseRequest(BaseModel):
    """请求体：地产标的、用户画像、户籍、可选基准日与 LLM/图参数。"""
    property_of_interest: str = Field(..., description="地产标的（区域、楼盘、具体地址等）")
    user_profile: str = Field(..., description="用户画像：预算、用途、是否非居住者、持有期限等")
    household_region: Optional[str] = Field(None, description="用户户籍/国籍/常居地，供政策研究员分析该国在日购房政策")
    trade_date: Optional[str] = Field(None, description="分析基准日 yyyy-mm-dd，默认今天")
    llm_config: Optional[LLMConfig] = Field(None, description="模型与 Token，不传则使用环境变量或后端默认")
    selected_analysts: Optional[List[str]] = Field(
        None,
        description="参与的分析师：location, legal, policy, tax, yield，少开可降 429",
    )
    use_risk_debate: Optional[bool] = Field(
        None,
        description="True=三方风控辩论后裁判，False=仅风控裁判一人评判（省调用、推荐限流时用）",
    )
    debug: Optional[bool] = Field(False, description="是否开启调试")
    max_debate_rounds: Optional[int] = Field(None, description="多空辩论轮数")
    max_risk_discuss_rounds: Optional[int] = Field(None, description="风控辩论轮数")


class TokenUsage(BaseModel):
    """本次请求累计的 LLM token 用量。"""
    prompt_tokens: int = Field(0, description="输入 token 数")
    completion_tokens: int = Field(0, description="输出 token 数")
    total_tokens: int = Field(0, description="总 token 数")


class AdviseResponse(BaseModel):
    """响应：最终决策、信号、及各报告与计划摘要、token 用量。"""
    signal: str = Field(..., description="BUY | HOLD | AVOID")
    final_decision: str = Field(..., description="风控裁判完整结论")
    investment_plan: str = Field("", description="研究经理投资计划")
    trader_investment_plan: str = Field("", description="交易员可执行计划")
    location_report: str = Field("", description="区域报告摘要")
    legal_report: str = Field("", description="法律报告摘要")
    policy_report: str = Field("", description="政策研究员报告（户籍国在日购房政策）")
    tax_report: str = Field("", description="税务报告摘要")
    yield_report: str = Field("", description="收益报告摘要")
    token_usage: Optional[TokenUsage] = Field(None, description="本次请求消耗的 token 统计")


# ---------- 配置 schema（供前端展示可选参数） ----------


class ConfigSchemaResponse(BaseModel):
    """GET /config 返回的配置说明，便于前端生成表单。"""
    llm_providers: List[str] = Field(
        default=["openai", "openrouter", "ollama"],
        description="支持的 LLM 厂商（兼容 OpenAI API 的如 minimax 选 openai + backend_url）",
    )
    analyst_options: List[str] = Field(
        default=["location", "legal", "policy", "tax", "yield"],
        description="可选分析师类型",
    )
    advise_request_fields: Dict[str, str] = Field(
        default_factory=lambda: {
            "property_of_interest": "地产标的（必填）",
            "user_profile": "用户画像（必填）",
            "household_region": "用户户籍/国籍/常居地（可选，供政策研究员）",
            "trade_date": "分析基准日 yyyy-mm-dd（可选）",
            "llm_config.provider": "LLM 厂商",
            "llm_config.deep_think_llm": "深思模型名",
            "llm_config.quick_think_llm": "快思模型名",
            "llm_config.api_key": "API Key / Token",
            "llm_config.backend_url": "API 基地址（如 MiniMax）",
            "selected_analysts": "参与的分析师列表",
            "use_risk_debate": "True=三方风控辩论，False=仅风控裁判一人",
            "max_debate_rounds": "多空辩论轮数",
            "max_risk_discuss_rounds": "风控辩论轮数",
        },
    )


@app.get("/config", response_model=ConfigSchemaResponse)
def get_config_schema() -> ConfigSchemaResponse:
    """返回前端可用的参数说明，用于表单与联调。"""
    return ConfigSchemaResponse()


@app.post("/advise", response_model=AdviseResponse)
def advise(req: AdviseRequest) -> AdviseResponse:
    """
    运行多 Agent 图，返回最终建议与各报告。
    若传 llm_config，将使用前端提供的模型与 Token（如 MiniMax）；否则使用后端默认或环境变量。
    """
    log_step("API", "收到 POST /advise 请求", extra=f"标的: {(req.property_of_interest[:50] + '...') if len(req.property_of_interest) > 50 else req.property_of_interest}")
    llm_dict: Optional[Dict[str, Any]] = None
    if req.llm_config:
        llm_dict = req.llm_config.model_dump(exclude_none=True)
        if req.llm_config.provider and req.llm_config.provider.lower() == "minimax":
            llm_dict["provider"] = "openai"
            llm_dict.setdefault("backend_url", "https://api.minimax.chat/v1")
    graph = get_or_create_graph(
        llm_config=llm_dict,
        selected_analysts=req.selected_analysts,
        use_risk_debate=req.use_risk_debate,
        debug=req.debug or False,
        max_debate_rounds=req.max_debate_rounds,
        max_risk_discuss_rounds=req.max_risk_discuss_rounds,
    )
    token_cb = TokenUsageCallback()
    final_state, signal = graph.propagate(
        property_of_interest=req.property_of_interest,
        user_profile=req.user_profile,
        trade_date=req.trade_date,
        household_region=req.household_region or "",
        request_callbacks=[token_cb],
    )
    token_usage = TokenUsage(**token_cb.to_dict()) if (token_cb.prompt_tokens or token_cb.completion_tokens) else None
    return AdviseResponse(
        signal=signal,
        final_decision=final_state.get("final_decision") or "",
        investment_plan=final_state.get("investment_plan") or "",
        trader_investment_plan=final_state.get("trader_investment_plan") or "",
        location_report=final_state.get("location_report") or "",
        legal_report=final_state.get("legal_report") or "",
        policy_report=final_state.get("policy_report") or "",
        tax_report=final_state.get("tax_report") or "",
        yield_report=final_state.get("yield_report") or "",
        token_usage=token_usage,
    )


@app.get("/health")
def health() -> Dict[str, str]:
    return {"status": "ok"}
