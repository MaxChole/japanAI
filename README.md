# JapanAI — 日本地产投资建议后端

多角色 Agent 后端：通过「区域 / 法律 / 税务 / 收益」四类分析师 + 多空辩论 + 研究经理 + 交易员 + 风控辩论 + 风控裁判，产出 **BUY / HOLD / AVOID** 及可执行建议。

## 快速开始

**默认已使用 MiniMax 大模型与 Token（已写死后端），无需再配 OpenAI。**

```bash
# 安装依赖
pip3 install -r requirements.txt

# 启动 API 服务（默认 MiniMax abab6.5s-chat + 已配置 Token）
python3 run_api.py
# 服务地址: http://localhost:8000

# 测试「日本价格」查询（另开终端）
./scripts/test_advise.sh
# 或
python3 scripts/test_advise.py
```

若需改用其他模型或 Token，可设置环境变量 `MINIMAX_API_KEY`，或在前端/请求里传 `llm_config`。

## 请求示例

```json
POST /advise
{
  "property_of_interest": "东京都港区 某公寓，投资用",
  "user_profile": "预算约 5000 万日元，投资用途，非居住者，计划长期持有",
  "trade_date": "2025-02-24"
}
```

响应包含 `signal`（BUY/HOLD/AVOID）、`final_decision`、各报告与计划摘要。

## 文档与注释

- **[ARCHITECTURE.md](ARCHITECTURE.md)**：架构说明、数据流、图编排、扩展建议（含注释）。
- 各模块内关键逻辑已加中文注释，便于阅读与二次开发。

## 前端与联调

- **前端**：`frontend/` 为 Vite + React 单页应用，科技感 UI，支持所有后端参数（标的、用户画像、模型与 Token、图参数等），厂商可选 OpenAI / MiniMax / OpenRouter / Ollama / 自定义。
- **启动前端**：`cd frontend && npm install && npm run dev`，默认 http://localhost:5173。
- **前后端联调**：见 **[docs/FRONTEND_BACKEND_INTEGRATION.md](docs/FRONTEND_BACKEND_INTEGRATION.md)**，含 API 说明、参数表、MiniMax 示例与检查清单。

## 项目结构概览

- `japanai/agents/` — 状态、记忆、四类分析师、Bull/Bear、研究经理、交易员、风控辩论与裁判
- `japanai/dataflows/` — 数据层（当前 mock，可扩展真实 API）
- `japanai/llm_clients/` — LLM 工厂（openai / ollama / openrouter）
- `japanai/graph/` — 图编排、条件边、初始状态、信号解析
- `japanai/api/` — FastAPI `POST /advise`、`GET /config`、`GET /health`
- `frontend/` — React 前端，模型与 Token 由前端输入
- `docs/FRONTEND_BACKEND_INTEGRATION.md` — 前端后端连调文档

架构设计参考 TradingAgents 的 Agent/图/数据流模式。
