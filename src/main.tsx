import { FormEvent, ReactNode, useEffect, useState } from 'react'
import { createRoot } from 'react-dom/client'
import './styles.css'

type Account = { id: number; name: string; kind: string; balance: number }
type Debt = { id: number; name: string; balance: number; interest_rate: number; minimum_payment: number; due_day: number }
type Cashflow = { id: number; name: string; kind: 'income' | 'expense'; amount: number; due_day?: number; provider?: string }
type Goal = { id: number; name: string; target: number; current: number; due_date?: string }
type Summary = { assets: number; debt: number; available: number; monthly_income: number; monthly_expenses: number; monthly_surplus: number; recommended_debt_payment: number; accounts: Account[]; debts: Debt[]; cashflow: Cashflow[]; goals: Goal[] }
type EmailDocument = { id: number; sender: string; subject: string; received_at?: string; original_filename: string; status: string; created_at: string }
type Invoice = { id: number; provider: string; invoice_number: string; issue_date?: string; total: number; currency: string; status: string; source_xml?: string; source_pdf?: string }

const money = (value: number) => new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD' }).format(value)
const API = '/api'

function App() {
  const [summary, setSummary] = useState<Summary | null>(null)
  const [error, setError] = useState('')
  const [accountName, setAccountName] = useState('')
  const [accountBalance, setAccountBalance] = useState('')
  const [debtName, setDebtName] = useState('')
  const [debtBalance, setDebtBalance] = useState('')
  const [debtRate, setDebtRate] = useState('')
  const [debtMinimum, setDebtMinimum] = useState('')
  const [debtDue, setDebtDue] = useState('')
  const [cashflowName, setCashflowName] = useState('')
  const [cashflowAmount, setCashflowAmount] = useState('')
  const [goalName, setGoalName] = useState('')
  const [goalTarget, setGoalTarget] = useState('')
  const [documents, setDocuments] = useState<EmailDocument[]>([])
  const [emailMessage, setEmailMessage] = useState('')
  const [invoices, setInvoices] = useState<Invoice[]>([])

  const load = () => fetch(`${API}/summary`).then(r => { if (!r.ok) throw new Error('api'); return r.json() }).then(setSummary).catch(() => setError(`No responde la API en ${API}. Verifica que el backend esté iniciado y el puerto 8000 sea accesible.`))
  useEffect(load, [])
  useEffect(() => { fetch(`${API}/email/documents`).then(r => r.json()).then(data => setDocuments(data.documents ?? [])).catch(() => undefined) }, [])
  useEffect(() => { fetch(`${API}/invoices`).then(r => r.json()).then(data => setInvoices(data.invoices ?? [])).catch(() => undefined) }, [])

  const syncEmail = async () => {
    setEmailMessage('Sincronizando…')
    const response = await fetch(`${API}/email/sync`, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: '{}' })
    const data = await response.json()
    if (!response.ok) { setEmailMessage(data.error || 'No se pudo sincronizar el correo'); return }
    setDocuments(current => [...data.imported, ...current])
    setEmailMessage(`${data.count} documento(s) nuevo(s). Quedan pendientes de revisión.`)
  }

  const submitAccount = async (event: FormEvent) => {
    event.preventDefault()
    await fetch(`${API}/accounts`, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ name: accountName, balance: Number(accountBalance), kind: 'cash' }) })
    setAccountName(''); setAccountBalance(''); load()
  }
  const submitDebt = async (event: FormEvent) => {
    event.preventDefault()
    await fetch(`${API}/debts`, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ name: debtName, balance: Number(debtBalance), interest_rate: Number(debtRate), minimum_payment: Number(debtMinimum), due_day: Number(debtDue) }) })
    setDebtName(''); setDebtBalance(''); setDebtRate(''); setDebtMinimum(''); setDebtDue(''); load()
  }
  const submitCashflow = async (event: FormEvent, kind: 'incomes' | 'expenses') => {
    event.preventDefault()
    await fetch(`${API}/${kind}`, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ name: cashflowName, amount: Number(cashflowAmount) }) })
    setCashflowName(''); setCashflowAmount(''); load()
  }
  const submitGoal = async (event: FormEvent) => {
    event.preventDefault()
    await fetch(`${API}/goals`, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ name: goalName, target: Number(goalTarget), current: 0 }) })
    setGoalName(''); setGoalTarget(''); load()
  }

  return <main className="shell">
    <header className="hero"><div><p className="eyebrow">PANEL FINANCIERO LOCAL</p><h1>Budget Lens</h1><p className="sub">Una vista clara para decidir qué pagar, ahorrar y conservar.</p></div><span className="privacy">● Datos en tu equipo</span></header>
    {error && <div className="notice">{error}</div>}
    <section className="metrics">
      <Metric label="Dinero disponible" value={money(summary?.available ?? 0)} tone="green" hint="Activos menos pagos mínimos" />
      <Metric label="Patrimonio líquido" value={money((summary?.assets ?? 0) - (summary?.debt ?? 0))} hint="Cuentas menos deudas" />
      <Metric label="Pago recomendado" value={money(summary?.recommended_debt_payment ?? 0)} tone="blue" hint="Mínimos + capacidad disponible" />
      <Metric label="Deuda total" value={money(summary?.debt ?? 0)} tone="red" hint="Saldo pendiente registrado" />
      <Metric label="Superávit mensual" value={money(summary?.monthly_surplus ?? 0)} tone={summary?.monthly_surplus && summary.monthly_surplus < 0 ? 'red' : 'green'} hint="Ingresos menos gastos recurrentes" />
    </section>
    <section className="grid">
      <article className="card wide"><div className="card-title"><div><p className="eyebrow">PRÓXIMA DECISIÓN</p><h2>Prioridad de pago</h2></div><span className="badge">Avalanche</span></div>
        {summary?.debts?.length ? <div className="recommendation"><strong>{summary.debts[0].name}</strong><p>Registra el pago mínimo de {money(summary.debts[0].minimum_payment)} antes del día {summary.debts[0].due_day}. Su tasa registrada es {summary.debts[0].interest_rate}%.</p></div> : <div className="empty">Agrega tu primera deuda para recibir una recomendación explicable.</div>}
      </article>
      <article className="card"><p className="eyebrow">CUENTAS</p><h2>Liquidez</h2>{summary?.accounts?.length ? summary.accounts.map(a => <div className="row" key={a.id}><span>{a.name}</span><strong>{money(a.balance)}</strong></div>) : <div className="empty">Todavía no hay cuentas registradas.</div>}</article>
      <article className="card"><p className="eyebrow">DEUDAS</p><h2>Orden sugerido</h2>{summary?.debts?.length ? summary.debts.map(d => <div className="row" key={d.id}><span>{d.name}<small>{d.interest_rate}% · vence día {d.due_day}</small></span><strong className="red">{money(d.balance)}</strong></div>) : <div className="empty">Registra tarjetas, préstamos o compromisos.</div>}</article>
      <article className="card"><p className="eyebrow">FLUJO MENSUAL</p><h2>Ingresos y gastos</h2>{summary?.cashflow?.length ? summary.cashflow.map(item => <div className="row" key={item.id}><span>{item.name}<small>{item.kind === 'income' ? 'Ingreso' : `Gasto recurrente${item.due_day ? ` · vence día ${item.due_day}` : ''}`}{item.provider ? ` · ${item.provider}` : ''}</small></span><strong className={item.kind === 'income' ? 'green-text' : 'red'}>{money(item.amount)}</strong></div>) : <div className="empty">Agrega sueldo, alquiler, servicios y otros movimientos fijos.</div>}</article>
      <article className="card"><p className="eyebrow">METAS</p><h2>Ahorro</h2>{summary?.goals?.length ? summary.goals.map(goal => <div className="row" key={goal.id}><span>{goal.name}<small>Meta: {money(goal.target)}</small></span><strong>{money(goal.current)}</strong></div>) : <div className="empty">Crea una meta para separar ahorro de dinero disponible.</div>}</article>
    </section>
    <section className="card email-card"><div className="card-title"><div><p className="eyebrow">ENTRADA DE DOCUMENTOS</p><h2>Correo financiero</h2></div><button onClick={syncEmail}>Sincronizar correo</button></div><p className="subtle">Solo se guardan localmente adjuntos permitidos de remitentes autorizados. Nada actualiza saldos automáticamente.</p>{emailMessage && <div className="email-message">{emailMessage}</div>}{documents.length ? documents.map(document => <div className="row" key={document.id}><span>{document.original_filename}<small>{document.sender} · {document.status === 'pending_review' ? 'Pendiente de revisión' : document.status}</small></span><strong>{document.received_at ? new Date(document.received_at).toLocaleDateString() : 'Sin fecha'}</strong></div>) : <div className="empty">No hay documentos descargados desde el correo.</div>}</section>
    <section className="card invoice-card"><p className="eyebrow">FACTURAS PROCESADAS</p><h2>Gastos pendientes</h2>{invoices.length ? invoices.map(invoice => <div className="row" key={invoice.id}><span>{invoice.provider}<small>Factura {invoice.invoice_number} · {invoice.issue_date || 'Sin fecha'} · {invoice.status === 'pending_payment' ? 'Pendiente de pago' : invoice.status}</small></span><strong className="red">{money(invoice.total)}</strong></div>) : <div className="empty">Todavía no hay facturas procesadas.</div>}</section>
    <section className="forms"><Form title="Agregar cuenta" onSubmit={submitAccount}><input required placeholder="Ej. Cuenta principal" value={accountName} onChange={e => setAccountName(e.target.value)} /><input required type="number" step="0.01" placeholder="Saldo actual" value={accountBalance} onChange={e => setAccountBalance(e.target.value)} /><button>Guardar cuenta</button></Form><Form title="Agregar deuda" onSubmit={submitDebt}><input required placeholder="Ej. Visa" value={debtName} onChange={e => setDebtName(e.target.value)} /><input required type="number" step="0.01" placeholder="Saldo" value={debtBalance} onChange={e => setDebtBalance(e.target.value)} /><div className="two"><input required type="number" step="0.01" placeholder="Tasa %" value={debtRate} onChange={e => setDebtRate(e.target.value)} /><input required type="number" placeholder="Día de pago" value={debtDue} onChange={e => setDebtDue(e.target.value)} /></div><input required type="number" step="0.01" placeholder="Pago mínimo" value={debtMinimum} onChange={e => setDebtMinimum(e.target.value)} /><button>Guardar deuda</button></Form><Form title="Agregar ingreso" onSubmit={e => submitCashflow(e, 'incomes')}><input required placeholder="Ej. Salario" value={cashflowName} onChange={e => setCashflowName(e.target.value)} /><input required type="number" step="0.01" placeholder="Monto mensual" value={cashflowAmount} onChange={e => setCashflowAmount(e.target.value)} /><button>Guardar ingreso</button></Form><Form title="Agregar gasto fijo" onSubmit={e => submitCashflow(e, 'expenses')}><input required placeholder="Ej. Alquiler" value={cashflowName} onChange={e => setCashflowName(e.target.value)} /><input required type="number" step="0.01" placeholder="Monto mensual" value={cashflowAmount} onChange={e => setCashflowAmount(e.target.value)} /><button>Guardar gasto</button></Form><Form title="Agregar meta de ahorro" onSubmit={submitGoal}><input required placeholder="Ej. Fondo de emergencia" value={goalName} onChange={e => setGoalName(e.target.value)} /><input required type="number" step="0.01" placeholder="Monto objetivo" value={goalTarget} onChange={e => setGoalTarget(e.target.value)} /><button>Guardar meta</button></Form></section>
  </main>
}

function Metric({ label, value, hint, tone = '' }: { label: string; value: string; hint: string; tone?: string }) { return <div className={`metric ${tone}`}><p>{label}</p><strong>{value}</strong><small>{hint}</small></div> }
function Form({ title, children, onSubmit }: { title: string; children: ReactNode; onSubmit: (e: FormEvent) => void }) { return <form className="card form" onSubmit={onSubmit}><p className="eyebrow">REGISTRO MANUAL</p><h2>{title}</h2>{children}</form> }

createRoot(document.getElementById('root')!).render(<App />)
