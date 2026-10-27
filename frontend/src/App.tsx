import { useState } from 'react'
import {
  Activity,
  ArrowUpRight,
  BookOpen,
  Bot,
  CheckCircle2,
  ChevronDown,
  CircleHelp,
  FileText,
  Gauge,
  LayoutDashboard,
  Menu,
  MessageSquare,
  Plus,
  Send,
  Settings,
  ShieldCheck,
  Sparkles,
  Wallet,
  X,
  Clock3,
  AlertCircle,
  Database,
  RefreshCw,
} from 'lucide-react'
import './App.css'
import ReactMarkdown from 'react-markdown';
type MetricsSummary = {
  status?: string;
  requests?: Record<string, {
    request_count?: number;
    total_duration_ms?: number;
    average_duration_ms?: number;
    slow_request_count?: number;
  }>;
  rag?: {
    request_count?: number;
    average_retrieval_duration_ms?: number;
    average_llm_duration_ms?: number;
    abstention_count?: number;
  };
  quality?: {
    average_evaluator_score?: number;
    evaluation_count?: number;
    positive_feedback_rate?: number;
    total_feedback?: number;
    positive_feedback?: number;
    negative_feedback?: number;
  };
  feedback?: {
    total_feedback?: number;
    positive_feedback?: number;
    negative_feedback?: number;
    positive_feedback_rate?: number;
  };
  business?: {
    accounting_questions_answered?: number;
    accounting_questions_abstained?: number;
    transaction_explanations?: number;
    total_accounting_questions?: number;
    answer_rate?: number;
  };
};
type Source = Record<string, unknown>

type AccountingResult = {
  response?: string
  journal_entry?: {
    description?: string
    debit?: { account?: string; amount?: number }
    credit?: { account?: string; amount?: number }
  } | null
  sources?: Source[]
  confidence?: number
}

const API_BASE = (import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000').replace(/\/$/, '')

function readable(value: unknown): string {
  if (value === null || value === undefined || value === '') return 'Not provided'
  if (typeof value === 'string' || typeof value === 'number' || typeof value === 'boolean') return String(value)
  return JSON.stringify(value)
}

function sourceName(source: Source, index: number): string {
  return readable(source.source ?? source.filename ?? source.file ?? source.document ?? `Source ${index + 1}`)
}

function App() {
  const [activePage, setActivePage] = useState('Overview')
  const [mobileNavOpen, setMobileNavOpen] = useState(false)
  const [prompt, setPrompt] = useState('')
  const [transaction, setTransaction] = useState('')
  const [result, setResult] = useState<AccountingResult | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [metrics, setMetrics] = useState<MetricsSummary | null>(null)
  const [metricsState, setMetricsState] = useState<'idle' | 'loaded' | 'disabled' | 'error'>('idle')
  const [health, setHealth] = useState<'checking' | 'healthy' | 'error'>('checking')
  const [notice, setNotice] = useState('')

  async function checkHealth() {
    setHealth('checking')
    try {
      const response = await fetch(`${API_BASE}/health`)
      if (!response.ok) throw new Error('Backend health check failed')
      setHealth('healthy')
    } catch {
      setHealth('error')
    }
  }

  async function loadMetrics() {
    setMetricsState('idle')
    try {
      const response = await fetch(`${API_BASE}/metrics/summary`)
      const data = await response.json()
      if (!response.ok || data.status === 'disabled') {
        setMetricsState('disabled')
        setMetrics(data)
        return
      }
      setMetrics(data)
      setMetricsState('loaded')
    } catch {
      setMetricsState('error')
    }
  }

  async function askAccounting(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault()
    if (!prompt.trim()) return
    setLoading(true)
    setError('')
    setNotice('')
    setResult(null)
    try {
      const response = await fetch(`${API_BASE}/accounting/intelligence`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ prompt: prompt.trim() }),
      })
      const data = await response.json()
      if (!response.ok) throw new Error(data.detail || `Request failed (${response.status})`)
      setResult(data)
      setActivePage('AI Assistant')
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unable to reach the accounting API.')
    } finally {
      setLoading(false)
    }
  }

  async function explainTransaction(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault()
    if (!transaction.trim()) return
    setLoading(true)
    setError('')
    setNotice('')
    setResult(null)
    try {
      const response = await fetch(`${API_BASE}/accounting/transaction/explain`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ description: transaction.trim() }),
      })
      const data = await response.json()
      if (!response.ok) throw new Error(data.detail || `Request failed (${response.status})`)
      setResult(data)
      setActivePage('Transactions')
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unable to reach the accounting API.')
    } finally {
      setLoading(false)
    }
  }

  function navigate(page: string) {
    setActivePage(page)
    setMobileNavOpen(false)
    setError('')
    setNotice('')
    if (page === 'Overview') {
      void checkHealth()
      void loadMetrics()
    }
    if (page !== 'AI Assistant' && page !== 'Transactions') setResult(null)
  }

  // Check backend status when the dashboard first opens.
  useState(() => {
    void checkHealth()
    void loadMetrics()
  })

  const navGroups = [
    {
      title: 'WORKSPACE',
      items: [
        { label: 'Overview', icon: LayoutDashboard },
        { label: 'AI Assistant', icon: MessageSquare },
        { label: 'Transactions', icon: Wallet },
        { label: 'Knowledge Base', icon: BookOpen },
      ],
    },
    {
      title: 'INTELLIGENCE',
      items: [
        { label: 'Evaluations', icon: Gauge },
        { label: 'Monitoring', icon: Activity },
        { label: 'Audit & Safety', icon: ShieldCheck },
      ],
    },
  ]

  const isAssistant = activePage === 'AI Assistant'
  const isTransactions = activePage === 'Transactions'
  const confidence = typeof result?.confidence === 'number'
    ? `${Math.round((result.confidence ?? 0) * 100)}%`
    : '—'

  return (
    <div className="app-shell">
      {mobileNavOpen && <button className="mobile-scrim" aria-label="Close navigation" onClick={() => setMobileNavOpen(false)} />}
      <aside className={`sidebar ${mobileNavOpen ? 'sidebar-open' : ''}`}>
        <div className="brand">
          <div className="brand-mark"><Sparkles size={21} /></div>
          <div><div className="brand-name">LedgerAI</div><div className="brand-caption">ACCOUNTING COPILOT</div></div>
          <button className="icon-button mobile-close" aria-label="Close navigation" onClick={() => setMobileNavOpen(false)}><X size={18} /></button>
        </div>

        <div className="workspace-switcher">
          <div className="workspace-icon"><Wallet size={17} /></div>
          <div className="workspace-copy"><strong>Finance workspace</strong><span>Local environment</span></div>
          <ChevronDown size={15} className="muted-icon" />
        </div>

        <nav className="navigation">
          {navGroups.map((group) => (
            <div className="nav-group" key={group.title}>
              <div className="nav-heading">{group.title}</div>
              {group.items.map(({ label, icon: Icon }) => (
                <button key={label} className={`nav-link ${activePage === label ? 'nav-link-active' : ''}`} onClick={() => navigate(label)}>
                  <Icon size={18} strokeWidth={1.8} />
                  <span>{label}</span>
                  {label === 'AI Assistant' && <span className="nav-new">AI</span>}
                </button>
              ))}
            </div>
          ))}
        </nav>

        <div className="sidebar-bottom">
          <div className="sidebar-tip">
            <div className="tip-icon"><ShieldCheck size={18} /></div>
            <strong>Evidence first</strong>
            <p>Accounting answers are grounded in your local knowledge base.</p>
          </div>
          <button className="nav-link" onClick={() => navigate('Settings')}><Settings size={18} /><span>Settings</span></button>
          <div className="profile-row">
            <div className="avatar">AC</div>
            <div className="profile-copy"><strong>Accounting Copilot</strong><span>Local instance</span></div>
            <span className="online-dot" title="Local app" />
          </div>
        </div>
      </aside>

      <main className="main-area">
        <header className="topbar">
          <div className="topbar-left">
            <button className="icon-button mobile-menu" aria-label="Open navigation" onClick={() => setMobileNavOpen(true)}><Menu size={20} /></button>
            <div className="breadcrumbs"><span>Workspace</span><span className="crumb-slash">/</span><strong>{activePage}</strong></div>
          </div>
          <div className="topbar-right">
            <div className={`system-status ${health === 'healthy' ? 'status-good' : health === 'error' ? 'status-bad' : ''}`}>
              <span className="status-dot" />{health === 'healthy' ? 'API connected' : health === 'error' ? 'API unavailable' : 'Checking API'}
            </div>
            <button className="icon-button" aria-label="Refresh backend status" onClick={() => { void checkHealth(); void loadMetrics() }}><RefreshCw size={17} /></button>
            <div className="top-avatar">AC</div>
          </div>
        </header>

        <div className="page-content">
          {activePage === 'Overview' && (
            <>
              <section className="welcome-row">
                <div><div className="eyebrow"><span className="eyebrow-line" /> YOUR ACCOUNTING WORKSPACE</div><h1>Good evening. <span>Let's make sense of the numbers.</span></h1><p className="page-subtitle">Your AI-powered workspace for grounded accounting answers and transaction intelligence.</p></div>
                <div className="date-chip"><Clock3 size={15} /> Local environment</div>
              </section>

              <section className="hero-card">
                <div className="hero-content">
                  <div className="hero-tag"><Sparkles size={14} /> YOUR AI ACCOUNTING ASSISTANT</div>
                  <h2>Accounting clarity,<br /><span>without the guesswork.</span></h2>
                  <p>Ask accounting questions, understand transactions, and explore supporting evidence — all powered by your local AI stack.</p>
                  <button className="hero-button" onClick={() => navigate('AI Assistant')}>Ask your copilot <span>→</span></button>
                </div>
                <div className="hero-art" aria-hidden="true">
                  <div className="orbit orbit-one" /><div className="orbit orbit-two" />
                  <div className="art-card art-card-back"><div className="art-mini-label">EVIDENCE RETRIEVAL</div><div className="art-line long" /><div className="art-line medium" /><div className="art-line short" /><div className="art-pill"><CheckCircle2 size={12} /> Sources found</div></div>
                  <div className="art-card art-card-front"><div className="art-card-top"><div className="art-icon"><Bot size={19} /></div><span className="art-live"><span /> LIVE</span></div><div className="art-mini-label">ACCOUNTING INSIGHT</div><div className="art-line long" /><div className="art-line medium" /><div className="art-score"><div><span>Retrieval confidence</span><strong>{confidence}</strong></div><div className="score-track"><span style={{ width: result ? `${Math.max(0, Math.min(100, (result.confidence ?? 0) * 100))}%` : '0%' }} /></div></div></div>
                  <div className="floating-symbol symbol-one">✳</div><div className="floating-symbol symbol-two">+</div>
                </div>
              </section>

              <section className="section-heading"><div><h2>Workspace overview</h2><p>A live view of your local accounting AI service.</p></div><button className="text-button" onClick={() => { void checkHealth(); void loadMetrics() }}><RefreshCw size={14} /> Refresh data</button></section>
              <section className="metrics-grid">
                <MetricCard icon={<Activity size={18} />} label="API status" value={health === 'healthy' ? 'Operational' : health === 'error' ? 'Offline' : 'Checking'} detail={health === 'healthy' ? 'Health endpoint responded' : health === 'error' ? 'Check FastAPI server' : 'Connecting to backend'} tone={health === 'error' ? 'red' : 'green'} />
                <MetricCard icon={<Gauge size={18} />} label="Evaluation metrics" value={metricsState === 'loaded' ? 'Available' : metricsState === 'disabled' ? 'Disabled' : metricsState === 'error' ? 'Unavailable' : 'Loading'} detail={metricsState === 'loaded' ? 'Live metrics retrieved' : 'From /metrics/summary'} tone="blue" />
                <MetricCard icon={<Database size={18} />} label="Knowledge retrieval" value="RAG enabled" detail="Local knowledge sources" tone="purple" />
                <MetricCard icon={<ShieldCheck size={18} />} label="AI safety" value="Evidence-led" detail="Confidence and abstention" tone="amber" />
              </section>

              <section className="lower-grid">
                <div className="panel quick-panel"><div className="panel-heading"><div><h3>Quick actions</h3><p>Jump straight into your workflow.</p></div><div className="panel-heading-icon"><Sparkles size={17} /></div></div>
                  <button className="quick-action" onClick={() => navigate('AI Assistant')}><div className="quick-icon quick-blue"><MessageSquare size={18} /></div><div><strong>Ask an accounting question</strong><span>Get a grounded explanation with sources</span></div><span className="quick-arrow">↗</span></button>
                  <button className="quick-action" onClick={() => navigate('Transactions')}><div className="quick-icon quick-green"><Wallet size={18} /></div><div><strong>Explain a transaction</strong><span>Understand the accounting treatment</span></div><span className="quick-arrow">↗</span></button>
                  <button className="quick-action" onClick={() => navigate('Monitoring')}><div className="quick-icon quick-violet"><Activity size={18} /></div><div><strong>Inspect system metrics</strong><span>Review monitoring endpoint status</span></div><span className="quick-arrow">↗</span></button>
                </div>
                <div className="panel readiness-panel"><div className="panel-heading"><div><h3>System readiness</h3><p>Connectivity checks for your local stack.</p></div><span className={`readiness-icon ${health === 'healthy' ? 'readiness-ok' : ''}`}>{health === 'healthy' ? <CheckCircle2 size={18} /> : <Activity size={18} />}</span></div>
                  <div className="readiness-row"><span className="readiness-name"><span className={`tiny-status ${health === 'healthy' ? 'tiny-good' : health === 'error' ? 'tiny-bad' : ''}`} />FastAPI backend</span><span className="readiness-value">{health === 'healthy' ? 'Connected' : health === 'error' ? 'Unavailable' : 'Checking'}</span></div>
                  <div className="readiness-row"><span className="readiness-name"><span className="tiny-status tiny-good" />Local knowledge base</span><span className="readiness-value">Configured</span></div>
                  <div className="readiness-row"><span className="readiness-name"><span className={`tiny-status ${metricsState === 'loaded' ? 'tiny-good' : ''}`} />Metrics endpoint</span><span className="readiness-value">{metricsState === 'loaded' ? 'Available' : metricsState === 'disabled' ? 'Disabled' : metricsState === 'error' ? 'Unavailable' : 'Checking'}</span></div>
                  <div className="readiness-note"><CircleHelp size={15} /><span>Use the readiness endpoint to verify database and Ollama connectivity.</span></div>
                </div>
              </section>
            </>
          )}

          {(isAssistant || isTransactions) && (
            <section className="work-page">
              <div className="work-intro"><div className="eyebrow"><span className="eyebrow-line" /> {isAssistant ? 'GROUNDED ACCOUNTING INTELLIGENCE' : 'TRANSACTION INTELLIGENCE'}</div><h1>{isAssistant ? 'Ask your copilot.' : 'Understand every transaction.'}</h1><p>{isAssistant ? 'Get clear accounting explanations backed by retrieved knowledge and source evidence.' : 'Explore the accounting treatment of a transaction and inspect any supported journal entry.'}</p></div>
              <div className="work-layout">
                <div className="panel query-panel">
                  <div className="query-panel-heading"><div className="query-icon"><Bot size={20} /></div><div><h3>{isAssistant ? 'Accounting assistant' : 'Transaction explainer'}</h3><p>{isAssistant ? 'Powered by your local RAG pipeline' : 'Classification and journal entry support'}</p></div><span className="local-pill">LOCAL AI</span></div>
                  <form onSubmit={isAssistant ? askAccounting : explainTransaction}>
                    <label htmlFor="accounting-input">{isAssistant ? 'What would you like to understand?' : 'Describe your transaction'}</label>
                    <textarea id="accounting-input" value={isAssistant ? prompt : transaction} onChange={e => isAssistant ? setPrompt(e.target.value) : setTransaction(e.target.value)} placeholder={isAssistant ? 'e.g. How do I record rent paid in cash?' : 'e.g. Paid office rent of 25000 in cash'} rows={5} />
                    <div className="input-helper"><span>Be specific for more relevant retrieval.</span><span>{(isAssistant ? prompt : transaction).length}/2000</span></div>
                    <button className="submit-button" type="submit" disabled={loading || !(isAssistant ? prompt.trim() : transaction.trim())}>{loading ? <><span className="spinner" /> Working with your local AI...</> : <><Send size={16} /> {isAssistant ? 'Generate explanation' : 'Explain transaction'} <span>→</span></>}</button>
                  </form>
                  <div className="example-block"><span className="example-label">TRY AN EXAMPLE</span><button onClick={() => { if (isAssistant) setPrompt('How do I record rent paid in cash?'); else setTransaction('Paid office rent of 25000 in cash') }}>{isAssistant ? 'How do I record rent paid in cash?' : 'Paid office rent of 25000 in cash'} <Plus size={14} /></button><button onClick={() => { if (isAssistant) setPrompt('Explain the difference between assets and expenses.'); else setTransaction('Purchased office supplies for 1200 in cash') }}>{isAssistant ? 'Explain assets vs. expenses' : 'Purchased office supplies for 1200 in cash'} <Plus size={14} /></button></div>
                </div>
                <div className="result-column">
                  {error && <div className="error-banner"><AlertCircle size={18} /><div><strong>Request unsuccessful</strong><p>{error}</p><span>Make sure FastAPI and your local Ollama service are running.</span></div></div>}
                  {notice && <div className="success-banner"><CheckCircle2 size={16} />{notice}</div>}
                  {!result && !error && <div className="panel empty-result"><div className="empty-illustration"><div className="empty-orbit" /><div className="empty-icon"><Sparkles size={26} /></div><span className="empty-spark spark-a">✦</span><span className="empty-spark spark-b">✧</span></div><h3>Your insights will appear here</h3><p>Submit a question to receive an explanation, retrieval confidence, and source details from your accounting knowledge base.</p><div className="empty-features"><span><CheckCircle2 size={14} /> Source-backed answers</span><span><ShieldCheck size={14} /> Evidence-aware output</span></div></div>}
                  {result && <div className="panel answer-panel"><div className="answer-topline"><span className="answer-label"><Sparkles size={15} /> AI RESPONSE</span><span className="answer-live"><span /> Generated</span></div><h3>Here's what I found</h3><div className="answer-body">
  <ReactMarkdown>
    {result.response || 'The API returned no explanation.'}
  </ReactMarkdown>
</div>
                    <div className="confidence-card"><div className="confidence-heading"><div><span className="small-overline">RETRIEVAL CONFIDENCE</span><strong>{confidence}</strong></div><span className="confidence-icon"><Gauge size={18} /></span></div><div className="confidence-track"><span style={{ width: result.confidence === undefined ? '0%' : `${Math.max(0, Math.min(100, result.confidence * 100))}%` }} /></div><p>This score reflects retrieval confidence; it is not a guarantee that the answer is correct.</p></div>
                    {result.journal_entry && <div className="journal-card"><div className="journal-title"><FileText size={17} /><strong>Suggested journal entry</strong></div><p>{result.journal_entry.description}</p><div className="journal-row journal-header"><span>ACCOUNT</span><span>DEBIT</span><span>CREDIT</span></div><div className="journal-row"><span>{result.journal_entry.debit?.account || '—'}</span><strong>{result.journal_entry.debit?.amount ?? '—'}</strong><span>—</span></div><div className="journal-row"><span>{result.journal_entry.credit?.account || '—'}</span><span>—</span><strong>{result.journal_entry.credit?.amount ?? '—'}</strong></div><div className="journal-balance"><CheckCircle2 size={14} /> Proposed entry — not approved. Verify the accounts and amount before posting.</div></div>}
                    <div className="sources-heading"><div><h4>Retrieved evidence</h4><p>Source details returned by your API</p></div><span className="source-count">{result.sources?.length ?? 0} sources</span></div>
                    {result.sources?.length ? <div className="source-list">{result.sources.map((source, index) => <div className="source-item" key={`${sourceName(source, index)}-${index}`}><div className="source-file-icon"><FileText size={17} /></div><div className="source-copy"><strong>{sourceName(source, index)}</strong><span>{source.chunk_id !== undefined ? `Chunk ${readable(source.chunk_id)}` : source.id !== undefined ? `ID ${readable(source.id)}` : 'Retrieved knowledge source'}</span>{source.content !== undefined && <p>{readable(source.content)}</p>}</div>{typeof source.similarity === 'number' && <span className="similarity-tag">{Math.round(source.similarity * 100)}% match</span>}</div>)}</div> : <div className="no-sources"><CircleHelp size={16} /> No source records were returned with this answer.</div>}
                    <div className="answer-disclaimer"><ShieldCheck size={15} /><span>AI-generated accounting guidance. Verify material decisions with your accounting policy and a qualified professional.</span></div>
                  </div>}
                </div>
              </div>
            </section>
          )}

          {activePage === 'Monitoring' && (
            
            <section className="work-page">
              <div className="work-intro"><div className="eyebrow"><span className="eyebrow-line" /> ACCOUNTING COPILOT</div><h1>{activePage}</h1><p>Explore the status and capabilities of your local accounting intelligence service.</p></div>
              <div className="panel placeholder-page"><div className="placeholder-icon"><BookOpen size={24} /></div><h3>{activePage} workspace</h3><p>This section is connected to the dashboard navigation. The backend currently exposes health, readiness, metrics, feedback, and protected audit endpoints. Further workflows can be added here without exposing private credentials in the browser.</p>
                <div className="endpoint-row"><code>GET /health</code><span>Service health</span><button onClick={() => { void checkHealth(); setNotice('Health check requested.') }}>Check <ArrowUpRight size={14} /></button></div>
                <div className="endpoint-row"><code>GET /ready</code><span>Database and Ollama readiness</span><button onClick={async () => { try { const r = await fetch(`${API_BASE}/ready`); const d = await r.json(); setNotice(`Readiness response: ${readable(d.status || r.status)}.`) } catch { setNotice('Could not reach the readiness endpoint.') } }}>Check <ArrowUpRight size={14} /></button></div>
                <div className="endpoint-row"><code>GET /metrics/summary</code><span>Monitoring summary</span><button onClick={async () => { await loadMetrics(); setNotice('Metrics request completed. See status on Overview.') }}>Check <ArrowUpRight size={14} /></button></div>
                {metrics && (
  <div className="monitoring-results">
    <div className="monitoring-cards">
      <div className="metric-card">
        <span>Total API requests</span>
        <strong>
          {Object.values(metrics.requests || {}).reduce(
            (total: number, item: any) => total + item.request_count,
            0
          )}
        </strong>
      </div>

      <div className="metric-card">
        <span>Accounting questions</span>
        <strong>{metrics.business?.total_accounting_questions ?? 0}</strong>
      </div>

      <div className="metric-card">
        <span>Average retrieval time</span>
        <strong>{metrics.rag?.average_retrieval_duration_ms ?? 0} ms</strong>
      </div>

      <div className="metric-card">
        <span>Slow AI requests</span>
        <strong>
          {metrics.requests?.['/accounting/intelligence']?.slow_request_count ?? 0}
        </strong>
      </div>
    </div>

    <h3>Endpoint performance</h3>

    <div className="table-wrap">
      <table>
        <thead>
          <tr>
            <th>Endpoint</th>
            <th>Requests</th>
            <th>Average duration</th>
            <th>Slow requests</th>
          </tr>
        </thead>
        <tbody>
          {Object.entries(metrics.requests || {}).map(
            ([endpoint, data]: [string, any]) => (
              <tr key={endpoint}>
                <td><code>{endpoint}</code></td>
                <td>{data.request_count}</td>
                <td>{data.average_duration_ms} ms</td>
                <td>{data.slow_request_count}</td>
              </tr>
            )
          )}
        </tbody>
      </table>
    </div>
  </div>
)}
              </div>
            </section>
            
          )}
          
          
{activePage === 'Evaluations' && (
  <section className="work-page">
    <div className="work-intro">
      <div className="eyebrow">
        <span className="eyebrow-line" />
        ACCOUNTING COPILOT
      </div>
      <h1>Evaluations</h1>
      <p>
        Review AI answer quality, evaluation coverage, and feedback
        using the metrics reported by the backend.
      </p>
    </div>

    <div className="monitoring-cards">
      <div className="metric-card">
        <span>Evaluations completed</span>
        <strong>{metrics?.quality?.evaluation_count ?? 0}</strong>
      </div>

      <div className="metric-card">
        <span>Average evaluator score</span>
        <strong>{metrics?.quality?.average_evaluator_score ?? 'N/A'}</strong>
      </div>

      <div className="metric-card">
        <span>Positive feedback</span>
        <strong>{metrics?.feedback?.positive_feedback ?? 0}</strong>
      </div>

      <div className="metric-card">
        <span>Total feedback</span>
        <strong>{metrics?.feedback?.total_feedback ?? 0}</strong>
      </div>
    </div>

    <div className="panel placeholder-page">
      <h3>Evaluation data</h3>
      <p>
        These figures come from the backend metrics endpoint.
        They are monitoring metrics, not a newly executed evaluation run.
      </p>
      <button
        onClick={async () => {
          await loadMetrics();
          setNotice('Evaluation metrics refreshed.');
        }}
      >
        Refresh metrics <ArrowUpRight size={14} />
      </button>
    </div>
  </section>
)}

{activePage === 'Knowledge Base' && (
  <section className="work-page">
    <div className="work-intro">
      <div className="eyebrow">
        <span className="eyebrow-line" />
        ACCOUNTING COPILOT
      </div>
      <h1>Knowledge Base</h1>
      <p>
        Explore the accounting knowledge used to ground AI-generated
        answers in relevant information.
      </p>
    </div>

    <div className="panel placeholder-page">
      <div className="placeholder-icon">
        <BookOpen size={24} />
      </div>
      <h3>Knowledge retrieval</h3>
      <p>
        Ask an accounting question in AI Assistant to retrieve relevant
        knowledge and inspect the sources returned with the answer.
        The knowledge documents and retrieval results are managed by
        the backend.
      </p>

      <div className="endpoint-row">
        <code>POST /accounting/intelligence</code>
        <span>Accounting question and source retrieval</span>
        <button onClick={() => setActivePage('AI Assistant')}>
          Open assistant <ArrowUpRight size={14} />
        </button>
      </div>
    </div>
  </section>
)}


{activePage === 'Audit & Safety' && (
  <section className="work-page">
    <div className="work-intro">
      <div className="eyebrow">
        <span className="eyebrow-line" />
        ACCOUNTING COPILOT
      </div>
      <h1>Audit &amp; Safety</h1>
      <p>
        Review service readiness, feedback signals, and safeguards
        for evidence-grounded accounting answers.
      </p>
    </div>

    <div className="monitoring-cards">
      <div className="metric-card">
        <span>Service status</span>
        <strong>
  {health === 'healthy'
    ? 'Healthy'
    : health === 'checking'
      ? 'Checking…'
      : health === 'error'
        ? 'Offline'
        : 'Unknown'}
</strong>
      </div>

      <div className="metric-card">
        <span>Evaluations recorded</span>
        <strong>{metrics?.quality?.evaluation_count ?? 0}</strong>
      </div>

      <div className="metric-card">
        <span>Negative feedback</span>
        <strong>{metrics?.feedback?.negative_feedback ?? 0}</strong>
      </div>

      <div className="metric-card">
        <span>Abstentions recorded</span>
        <strong>{metrics?.rag?.abstention_count ?? 0}</strong>
      </div>
    </div>

    <div className="panel placeholder-page">
      <h3>Safety and access controls</h3>
      <p>
        The assistant is designed to avoid inventing unsupported
        accounting rules when evidence is insufficient. Audit logs
        are protected by the backend and should not be accessed
        directly from browser code using a secret API key.
      </p>

      <div className="endpoint-row">
        <code>GET /ready</code>
        <span>Database and Ollama readiness</span>
        <button
          onClick={async () => {
            try {
              const response = await fetch(`${API_BASE}/ready`);
              const data = await response.json();
              setNotice(
                `Readiness: ${readable(data.status || response.status)}`
              );
            } catch {
              setNotice('Could not reach the readiness endpoint.');
            }
          }}
        >
          Check readiness <ArrowUpRight size={14} />
        </button>
      </div>
    </div>
  </section>
)}


{activePage === 'Settings' && (
  <section className="work-page">
    <div className="work-intro">
      <div className="eyebrow">
        <span className="eyebrow-line" />
        ACCOUNTING COPILOT
      </div>
      <h1>Settings</h1>
      <p>
        View your local workspace configuration and service
        connection details.
      </p>
    </div>

    <div className="panel placeholder-page">
      <div className="placeholder-icon">
        <Settings size={24} />
      </div>
      <h3>Workspace configuration</h3>

      <div className="endpoint-row">
        <span>Application</span>
        <strong>LedgerAI Accounting Copilot</strong>
      </div>

      <div className="endpoint-row">
        <span>Environment</span>
        <strong>Local development</strong>
      </div>

      <div className="endpoint-row">
        <span>Backend API</span>
        <code>{API_BASE}</code>
      </div>

      <div className="endpoint-row">
        <span>API connection</span>
        <strong>
          {health === 'healthy'
            ? 'Connected'
            : health === 'checking'
              ? 'Checking…'
              : health === 'error'
                ? 'Disconnected'
                : 'Not checked'}
        </strong>
      </div>

      <button
        onClick={async () => {
          await checkHealth();
          setNotice('Backend connection check requested.');
        }}
      >
        Check connection <ArrowUpRight size={14} />
      </button>

      <p>
        API addresses are configured through the frontend environment.
        Credentials and protected audit keys should remain on the backend.
      </p>
    </div>
  </section>
)}


          <footer className="page-footer"><span>LedgerAI <span className="footer-dot">·</span> AI Accounting Copilot</span><span><span className="footer-status" /> Local-first intelligence <span className="footer-dot">·</span> Powered by your own stack</span></footer>
        </div>
      </main>
    </div>
  )
}

function MetricCard({ icon, label, value, detail, tone }: { icon: React.ReactNode; label: string; value: string; detail: string; tone: string }) {
  return <div className="metric-card"><div className={`metric-icon metric-${tone}`}>{icon}</div><div className="metric-label">{label}</div><div className="metric-value">{value}</div><div className="metric-detail"><span className={`metric-detail-dot dot-${tone}`} />{detail}</div></div>
}

export default App
