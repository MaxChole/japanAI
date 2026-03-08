import { useState } from 'react'
import { advise, getConfigSchema, type AdviseRequest, type AdviseResponse, type ConfigSchema } from './api'
import styles from './App.module.css'

const ANALYST_OPTIONS = ['location', 'legal', 'policy', 'tax', 'yield'] as const
const PROVIDER_OPTIONS = [
  { value: 'openai', label: 'OpenAI' },
  { value: 'minimax', label: 'MiniMax' },
  { value: 'openrouter', label: 'OpenRouter' },
  { value: 'ollama', label: 'Ollama' },
  { value: 'custom', label: '自定义 (backend_url)' },
]

export default function App() {
  const [apiBase, setApiBase] = useState('http://localhost:8000')
  const [propertyOfInterest, setPropertyOfInterest] = useState('东京都港区 某公寓，投资用')
  const [userProfile, setUserProfile] = useState('预算约 5000 万日元，投资用途，非居住者，计划长期持有')
  const [householdRegion, setHouseholdRegion] = useState('中国')
  const [tradeDate, setTradeDate] = useState('')
  const [provider, setProvider] = useState('minimax')
  const [deepModel, setDeepModel] = useState('')
  const [quickModel, setQuickModel] = useState('')
  const [apiKey, setApiKey] = useState('')
  const [backendUrl, setBackendUrl] = useState('https://api.minimax.chat/v1')
  const [selectedAnalysts, setSelectedAnalysts] = useState<string[]>(['location', 'legal', 'tax', 'yield'])
  const [maxDebateRounds, setMaxDebateRounds] = useState(1)
  const [maxRiskRounds, setMaxRiskRounds] = useState(1)
  const [useRiskDebate, setUseRiskDebate] = useState(false)
  const [debug, setDebug] = useState(false)
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState<AdviseResponse | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [configSchema, setConfigSchema] = useState<ConfigSchema | null>(null)

  const toggleAnalyst = (a: string) => {
    setSelectedAnalysts((prev) =>
      prev.includes(a) ? prev.filter((x) => x !== a) : [...prev, a]
    )
  }

  const handleSubmit = async () => {
    setError(null)
    setResult(null)
    setLoading(true)
    try {
      const llmConfig: AdviseRequest['llm_config'] = {}
      if (provider && provider !== 'openai') {
        if (provider === 'minimax') {
          llmConfig.provider = 'minimax'
          llmConfig.backend_url = 'https://api.minimax.chat/v1'
          if (deepModel) llmConfig.deep_think_llm = deepModel
          if (quickModel) llmConfig.quick_think_llm = quickModel
          if (apiKey) llmConfig.api_key = apiKey
        } else if (provider === 'custom') {
          llmConfig.provider = 'openai'
          if (backendUrl) llmConfig.backend_url = backendUrl
          if (deepModel) llmConfig.deep_think_llm = deepModel
          if (quickModel) llmConfig.quick_think_llm = quickModel
          if (apiKey) llmConfig.api_key = apiKey
        } else {
          llmConfig.provider = provider
          if (deepModel) llmConfig.deep_think_llm = deepModel
          if (quickModel) llmConfig.quick_think_llm = quickModel
          if (apiKey) llmConfig.api_key = apiKey
          if (backendUrl && provider === 'openrouter') llmConfig.backend_url = backendUrl
        }
      } else if (provider === 'openai') {
        llmConfig.provider = 'openai'
        if (deepModel) llmConfig.deep_think_llm = deepModel
        if (quickModel) llmConfig.quick_think_llm = quickModel
        if (apiKey) llmConfig.api_key = apiKey
      }
      const payload: AdviseRequest = {
        property_of_interest: propertyOfInterest,
        user_profile: userProfile,
        household_region: householdRegion || undefined,
        trade_date: tradeDate || undefined,
        llm_config: Object.keys(llmConfig).length ? llmConfig : undefined,
        selected_analysts: selectedAnalysts.length ? selectedAnalysts : undefined,
        use_risk_debate: useRiskDebate,
        max_debate_rounds: maxDebateRounds,
        max_risk_discuss_rounds: maxRiskRounds,
        debug,
      }
      const res = await advise(apiBase, payload)
      setResult(res)
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : String(e))
    } finally {
      setLoading(false)
    }
  }

  const fetchConfig = async () => {
    try {
      const schema = await getConfigSchema(apiBase)
      setConfigSchema(schema)
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : String(e))
    }
  }

  return (
    <div className={styles.layout}>
      <header className={styles.header}>
        <h1 className={styles.title}>
          <span className={styles.brand}>JapanAI</span>
          <span className={styles.sub}>日本地产投资建议</span>
        </h1>
        <p className={styles.tagline}>多角色 Agent · BUY / HOLD / AVOID</p>
      </header>

      <div className={styles.content}>
        <aside className={styles.panel}>
          <section className={`glass glow ${styles.section}`}>
            <h2 className={styles.sectionTitle}>API 地址</h2>
            <input
              className={styles.input}
              value={apiBase}
              onChange={(e) => setApiBase(e.target.value)}
              placeholder="http://localhost:8000"
            />
            <button type="button" className={styles.btnSecondary} onClick={fetchConfig}>
              获取配置说明
            </button>
          </section>

          <section className={`glass glow ${styles.section}`}>
            <h2 className={styles.sectionTitle}>标的与用户</h2>
            <label className={styles.label}>地产标的 *</label>
            <textarea
              className={styles.textarea}
              value={propertyOfInterest}
              onChange={(e) => setPropertyOfInterest(e.target.value)}
              rows={2}
              placeholder="区域、楼盘等"
            />
            <label className={styles.label}>用户画像 *</label>
            <textarea
              className={styles.textarea}
              value={userProfile}
              onChange={(e) => setUserProfile(e.target.value)}
              rows={3}
              placeholder="预算、用途、是否非居住者、持有期限"
            />
            <label className={styles.label}>户籍/国籍/常居地（政策研究员用）</label>
            <input
              type="text"
              className={styles.input}
              value={householdRegion}
              onChange={(e) => setHouseholdRegion(e.target.value)}
              placeholder="如：中国、日本、美国"
            />
            <label className={styles.label}>分析基准日 (yyyy-mm-dd)</label>
            <input
              type="text"
              className={styles.input}
              value={tradeDate}
              onChange={(e) => setTradeDate(e.target.value)}
              placeholder="留空则今天"
            />
          </section>

          <section className={`glass glow ${styles.section}`}>
            <h2 className={styles.sectionTitle}>模型与 Token</h2>
            <label className={styles.label}>厂商</label>
            <select
              className={styles.select}
              value={provider}
              onChange={(e) => setProvider(e.target.value)}
            >
              {PROVIDER_OPTIONS.map((o) => (
                <option key={o.value} value={o.value}>{o.label}</option>
              ))}
            </select>
            {provider === 'minimax' && (
              <>
                <label className={styles.label}>深思模型 (如 abab6.5s)</label>
                <input
                  className={styles.input}
                  value={deepModel}
                  onChange={(e) => setDeepModel(e.target.value)}
                  placeholder="MiniMax 模型名"
                />
                <label className={styles.label}>快思模型</label>
                <input
                  className={styles.input}
                  value={quickModel}
                  onChange={(e) => setQuickModel(e.target.value)}
                  placeholder="可与深思相同"
                />
              </>
            )}
            {(provider === 'openai' || provider === 'custom' || provider === 'openrouter') && (
              <>
                <label className={styles.label}>深思模型</label>
                <input
                  className={styles.input}
                  value={deepModel}
                  onChange={(e) => setDeepModel(e.target.value)}
                  placeholder="如 gpt-4o-mini"
                />
                <label className={styles.label}>快思模型</label>
                <input
                  className={styles.input}
                  value={quickModel}
                  onChange={(e) => setQuickModel(e.target.value)}
                  placeholder="如 gpt-4o-mini"
                />
              </>
            )}
            {provider === 'custom' && (
              <>
                <label className={styles.label}>API 基地址</label>
                <input
                  className={styles.input}
                  value={backendUrl}
                  onChange={(e) => setBackendUrl(e.target.value)}
                  placeholder="https://api.xxx.com/v1"
                />
              </>
            )}
            <label className={styles.label}>API Key / Token *</label>
            <input
              type="password"
              className={styles.input}
              value={apiKey}
              onChange={(e) => setApiKey(e.target.value)}
              placeholder="前端传入，不落库"
            />
          </section>

          <section className={`glass glow ${styles.section}`}>
            <h2 className={styles.sectionTitle}>图参数</h2>
            <label className={styles.label}>参与分析师</label>
            <div className={styles.chipGroup}>
              {ANALYST_OPTIONS.map((a) => (
                <button
                  key={a}
                  type="button"
                  className={selectedAnalysts.includes(a) ? styles.chipActive : styles.chip}
                  onClick={() => toggleAnalyst(a)}
                >
                  {a}
                </button>
              ))}
            </div>
            <label className={styles.label}>多空辩论轮数</label>
            <input
              type="number"
              min={1}
              max={5}
              className={styles.input}
              value={maxDebateRounds}
              onChange={(e) => setMaxDebateRounds(Number(e.target.value))}
            />
            <label className={styles.label}>风控辩论轮数</label>
            <input
              type="number"
              min={1}
              max={5}
              className={styles.input}
              value={maxRiskRounds}
              onChange={(e) => setMaxRiskRounds(Number(e.target.value))}
            />
            <label className={styles.checkLabel}>
              <input
                type="checkbox"
                checked={useRiskDebate}
                onChange={(e) => setUseRiskDebate(e.target.checked)}
              />
              三方风控辩论（否则仅风控裁判一人）
            </label>
            <label className={styles.checkLabel}>
              <input
                type="checkbox"
                checked={debug}
                onChange={(e) => setDebug(e.target.checked)}
              />
              调试模式
            </label>
          </section>

          <button
            type="button"
            className={styles.submitBtn}
            onClick={handleSubmit}
            disabled={loading}
          >
            {loading ? '分析中…' : '获取建议'}
          </button>
        </aside>

        <main className={styles.resultArea}>
          {configSchema && (
            <div className={`glass ${styles.section}`}>
              <h3 className={styles.sectionTitle}>配置说明 (GET /config)</h3>
              <pre className={styles.pre}>{JSON.stringify(configSchema, null, 2)}</pre>
            </div>
          )}
          {error && (
            <div className={`glass ${styles.error}`}>
              <strong>错误</strong> {error}
            </div>
          )}
          {result && (
            <div className={`glass glow ${styles.result}`}>
              <div className={styles.signalWrap}>
                <span className={styles.signalLabel}>信号</span>
                <span className={`${styles.signal} ${styles[`signal_${result.signal.toLowerCase()}`]}`}>
                  {result.signal}
                </span>
                {result.token_usage && (
                  <div className={styles.tokenUsage}>
                    <span className={styles.tokenLabel}>Token 消耗</span>
                    <span className={styles.tokenValues}>
                      输入 {result.token_usage.prompt_tokens} · 输出 {result.token_usage.completion_tokens} · 合计 {result.token_usage.total_tokens}
                    </span>
                  </div>
                )}
              </div>
              <section className={styles.reportSection}>
                <h3>风控裁判结论</h3>
                <div className={`mono ${styles.reportText}`}>{result.final_decision}</div>
              </section>
              <section className={styles.reportSection}>
                <h3>投资计划</h3>
                <div className={`mono ${styles.reportText}`}>{result.investment_plan}</div>
              </section>
              <section className={styles.reportSection}>
                <h3>交易员计划</h3>
                <div className={`mono ${styles.reportText}`}>{result.trader_investment_plan}</div>
              </section>
              <section className={styles.reportSection}>
                <h3>区域报告</h3>
                <div className={`mono ${styles.reportText}`}>{result.location_report}</div>
              </section>
              <section className={styles.reportSection}>
                <h3>法律报告</h3>
                <div className={`mono ${styles.reportText}`}>{result.legal_report}</div>
              </section>
              <section className={styles.reportSection}>
                <h3>政策报告（户籍国在日购房政策）</h3>
                <div className={`mono ${styles.reportText}`}>{result.policy_report}</div>
              </section>
              <section className={styles.reportSection}>
                <h3>税务报告</h3>
                <div className={`mono ${styles.reportText}`}>{result.tax_report}</div>
              </section>
              <section className={styles.reportSection}>
                <h3>收益报告</h3>
                <div className={`mono ${styles.reportText}`}>{result.yield_report}</div>
              </section>
            </div>
          )}
          {!result && !error && !loading && (
            <div className={styles.placeholder}>
              填写左侧参数并点击「获取建议」，结果将在此展示。
            </div>
          )}
        </main>
      </div>
    </div>
  )
}
