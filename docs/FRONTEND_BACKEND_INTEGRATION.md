# JapanAI 前端与后端联调文档

本文档说明前端如何对接后端 API、所有可传参数、以及本地/生产联调方式。

---

## 一、服务启动

### 后端（FastAPI）

```bash
cd japanAI
pip install -r requirements.txt
python run_api.py
# 或: uvicorn japanai.api.app:app --host 0.0.0.0 --port 8000
```

默认地址：**http://localhost:8000**

- 健康检查：`GET http://localhost:8000/health`
- 配置说明：`GET http://localhost:8000/config`
- 投资建议：`POST http://localhost:8000/advise`

### 前端（Vite + React）

```bash
cd japanAI/frontend
npm install
npm run dev
```

默认地址：**http://localhost:5173**

前端页面「API 地址」输入框可修改后端基地址（如 `http://localhost:8000` 或生产环境 URL）。

---

## 二、API 说明

### 1. GET /config

返回前端可用的参数说明，用于表单与联调。

**响应示例：**

```json
{
  "llm_providers": ["openai", "openrouter", "ollama"],
  "analyst_options": ["location", "legal", "tax", "yield"],
  "advise_request_fields": {
    "property_of_interest": "地产标的（必填）",
    "user_profile": "用户画像（必填）",
    "trade_date": "分析基准日 yyyy-mm-dd（可选）",
    "llm_config.provider": "LLM 厂商",
    "llm_config.deep_think_llm": "深思模型名",
    "llm_config.quick_think_llm": "快思模型名",
    "llm_config.api_key": "API Key / Token",
    "llm_config.backend_url": "API 基地址（如 MiniMax）",
    "selected_analysts": "参与的分析师列表",
    "max_debate_rounds": "多空辩论轮数",
    "max_risk_discuss_rounds": "风控辩论轮数"
  }
}
```

### 2. POST /advise

请求体包含**标的与用户**（必填）以及**可选 LLM 配置与图参数**。后端会按需创建图实例（传入自定义配置时每次新建，否则复用默认图）。

#### 请求体字段（与后端一一对应）

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `property_of_interest` | string | 是 | 地产标的（区域、楼盘等） |
| `user_profile` | string | 是 | 用户画像：预算、用途、是否非居住者、持有期限等 |
| `trade_date` | string | 否 | 分析基准日 `yyyy-mm-dd`，不传则当天 |
| `llm_config` | object | 否 | 模型与 Token，见下表 |
| `selected_analysts` | string[] | 否 | 参与的分析师：`location`, `legal`, `tax`, `yield`，不传则四类全选 |
| `debug` | boolean | 否 | 是否调试模式，默认 false |
| `max_debate_rounds` | number | 否 | 多空辩论轮数，默认 1 |
| `max_risk_discuss_rounds` | number | 否 | 风控辩论轮数，默认 1 |

**llm_config 子字段：**

| 字段 | 类型 | 说明 |
|------|------|------|
| `provider` | string | `openai` \| `openrouter` \| `ollama` \| `minimax`（MiniMax 会转成 openai + backend_url） |
| `deep_think_llm` | string | 深思模型名（如 `gpt-4o-mini`、MiniMax 模型名） |
| `quick_think_llm` | string | 快思模型名 |
| `api_key` | string | API Key / Token，前端传入，后端仅当次请求使用、不落库 |
| `backend_url` | string | 自定义 API 基地址，如 MiniMax：`https://api.minimax.chat/v1` |

#### 使用 MiniMax 示例

前端选择厂商「MiniMax」时，请求体可设为：

```json
{
  "property_of_interest": "东京都港区 某公寓",
  "user_profile": "预算 5000 万日元，投资用，非居住者",
  "llm_config": {
    "provider": "minimax",
    "deep_think_llm": "abab6.5s",
    "quick_think_llm": "abab6.5s",
    "api_key": "你的 MiniMax API Key",
    "backend_url": "https://api.minimax.chat/v1"
  }
}
```

后端会将其转为 `provider: "openai"` + `backend_url` + `api_key` 调用兼容 OpenAI 的接口。

#### 响应体（AdviseResponse）

| 字段 | 类型 | 说明 |
|------|------|------|
| `signal` | string | 抽取的决策：`BUY` \| `HOLD` \| `AVOID` |
| `final_decision` | string | 风控裁判完整结论 |
| `investment_plan` | string | 研究经理投资计划 |
| `trader_investment_plan` | string | 交易员可执行计划 |
| `location_report` | string | 区域报告 |
| `legal_report` | string | 法律报告 |
| `tax_report` | string | 税务报告 |
| `yield_report` | string | 收益报告 |

---

## 三、前端表单与后端参数对应

前端已实现所有后端参数的可输入项：

- **API 地址**：对应请求发往的基地址（如 `http://localhost:8000`）。
- **标的与用户**：`property_of_interest`、`user_profile`、`trade_date`。
- **模型与 Token**：厂商（OpenAI / MiniMax / OpenRouter / Ollama / 自定义）、深思/快思模型名、API Key、自定义时还可填 `backend_url`。
- **图参数**：参与分析师多选、多空辩论轮数、风控辩论轮数、调试模式。

提交时前端会组装为上述 `POST /advise` 请求体；后端所有可配置项均可通过前端传入。

---

## 四、跨域与代理

- 后端已启用 **CORS**（`allow_origins=["*"]`），前端直接请求 `http://localhost:8000` 即可。
- 若希望同源请求，可在前端使用 Vite 代理：在 `vite.config.ts` 中已示例将 `/api` 代理到 `http://localhost:8000`，此时前端请求基地址填 `''` 或当前 origin，请求路径为 `/api/advise`、`/api/config`、`/api/health`；后端无需改动。

---

## 五、联调检查清单

1. 后端 `python run_api.py` 启动，访问 `http://localhost:8000/health` 返回 `{"status":"ok"}`。
2. 前端 `npm run dev` 启动，在页面将「API 地址」设为 `http://localhost:8000`。
3. 点击「获取配置说明」应成功拉取 `GET /config` 并展示。
4. 填写标的、用户画像，选择厂商（如 MiniMax）并填写对应模型名与 API Key，点击「获取建议」。
5. 确认 `POST /advise` 返回 200 且响应中 `signal`、`final_decision` 及各报告字段有内容；若 4xx/5xx，查看响应 body 或后端日志排查。

---

## 六、生产部署注意

- 前端生产构建：`cd frontend && npm run build`，将 `dist` 部署到静态托管或与后端同域。
- 生产环境建议将后端 API 基地址配置为环境变量或构建时注入，前端不再写死 `localhost`。
- API Key 仅由前端在当次请求中传给后端，后端不存储；若需更高安全性，可考虑后端代理或仅在后端配置环境变量。
