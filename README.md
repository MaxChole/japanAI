# JapanAI — 日本地产投资建议后端

多角色 Agent 后端：通过「区域 / 法律 / 税务 / 收益」四类分析师 + 多空辩论 + 研究经理 + 交易员 + 风控辩论 + 风控裁判，产出 **BUY / HOLD / AVOID** 及可执行建议。

## 快速开始

```bash
# 安装依赖
pip install -r requirements.txt

# 设置 OpenAI API Key 后直接运行一次图（命令行）
export OPENAI_API_KEY=your_key
python main.py

# 或启动 API 服务
python run_api.py
# 然后 POST http://localhost:8000/advise
```

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

## 项目结构概览

- `japanai/agents/` — 状态、记忆、四类分析师、Bull/Bear、研究经理、交易员、风控辩论与裁判
- `japanai/dataflows/` — 数据层（当前 mock，可扩展真实 API）
- `japanai/llm_clients/` — LLM 工厂（openai / ollama / openrouter）
- `japanai/graph/` — 图编排、条件边、初始状态、信号解析
- `japanai/api/` — FastAPI `POST /advise`

架构设计参考 [TradingAgents](https://github.com/...) 的 Agent/图/数据流模式。
