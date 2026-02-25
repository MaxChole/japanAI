/**
 * 前端调用后端 API：/advise、/config、/health
 * 所有后端参数均可通过 AdviseRequest 传入。
 */

export interface LLMConfig {
  provider?: string
  deep_think_llm?: string
  quick_think_llm?: string
  api_key?: string
  backend_url?: string
}

export interface AdviseRequest {
  property_of_interest: string
  user_profile: string
  trade_date?: string
  llm_config?: LLMConfig
  selected_analysts?: string[]
  debug?: boolean
  max_debate_rounds?: number
  max_risk_discuss_rounds?: number
}

export interface AdviseResponse {
  signal: string
  final_decision: string
  investment_plan: string
  trader_investment_plan: string
  location_report: string
  legal_report: string
  tax_report: string
  yield_report: string
}

export interface ConfigSchema {
  llm_providers: string[]
  analyst_options: string[]
  advise_request_fields: Record<string, string>
}

function base(apiBase: string) {
  return apiBase.replace(/\/$/, '')
}

export async function advise(apiBase: string, body: AdviseRequest): Promise<AdviseResponse> {
  const res = await fetch(`${base(apiBase)}/advise`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  })
  if (!res.ok) {
    const t = await res.text()
    throw new Error(t || `HTTP ${res.status}`)
  }
  return res.json()
}

export async function getConfigSchema(apiBase: string): Promise<ConfigSchema> {
  const res = await fetch(`${base(apiBase)}/config`)
  if (!res.ok) throw new Error(`HTTP ${res.status}`)
  return res.json()
}

export async function health(apiBase: string): Promise<{ status: string }> {
  const res = await fetch(`${base(apiBase)}/health`)
  if (!res.ok) throw new Error(`HTTP ${res.status}`)
  return res.json()
}
