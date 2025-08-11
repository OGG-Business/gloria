import React, { useEffect, useState } from 'react'
import axios from 'axios'

type Account = { id: number, iban: string, bic: string, display_name: string }

type Transfer = { id: number, status: 'INITIATED'|'PENDING'|'COMPLETED'|'FAILED', reference?: string }

type TransferEvent = { id: number, type: string, payload?: string }

const API = 'https://localhost:8443'

export default function App() {
  const [token, setToken] = useState<string>('')
  const [accounts, setAccounts] = useState<Account[]>([])
  const [selectedAccount, setSelectedAccount] = useState<number | null>(null)
  const [creditorIban, setCreditorIban] = useState('')
  const [creditorBic, setCreditorBic] = useState('')
  const [amount, setAmount] = useState('100.00')
  const [currency, setCurrency] = useState('USD')
  const [reference, setReference] = useState('Demo payment')
  const [dryRun, setDryRun] = useState(true)
  const [transfers, setTransfers] = useState<Transfer[]>([])
  const [events, setEvents] = useState<Record<number, TransferEvent[]>>({})

  const client = axios.create({ baseURL: API, headers: token ? { Authorization: `Bearer ${token}` } : {} })

  useEffect(() => {
    if (!token) return
    client.get<Account[]>('/accounts/').then(r => setAccounts(r.data))
    client.get<Transfer[]>('/transfers/').then(r => setTransfers(r.data))
  }, [token])

  const createTransfer = async () => {
    if (!selectedAccount) return alert('Select debtor account')
    const res = await client.post<Transfer>('/transfers/', {
      debtor_account_id: selectedAccount,
      creditor_iban: creditorIban,
      creditor_bic: creditorBic,
      amount: parseFloat(amount),
      currency,
      reference,
      dry_run: dryRun,
    })
    setTransfers([res.data, ...transfers])
  }

  const loadEvents = async (tid: number) => {
    const r = await client.get<TransferEvent[]>(`/transfers/${tid}/events`)
    setEvents({ ...events, [tid]: r.data })
  }

  return (
    <div className="container">
      <h1>Global Payments Platform</h1>
      <section className="card">
        <h2>Auth</h2>
        <input className="input" style={{ width: '100%' }} placeholder="Paste Bearer token (Keycloak)" value={token} onChange={e => setToken(e.target.value)} />
      </section>
      <section className="card">
        <h2>Initiate transfer</h2>
        <div className="grid grid-2">
          <div>
            <label>Debtor account</label>
            <select className="input" value={selectedAccount ?? ''} onChange={e => setSelectedAccount(parseInt(e.target.value))}>
              <option value="">Select</option>
              {accounts.map(a => <option key={a.id} value={a.id}>{a.display_name} - {a.iban}</option>)}
            </select>
          </div>
          <div>
            <label>Creditor IBAN</label>
            <input className="input" value={creditorIban} onChange={e => setCreditorIban(e.target.value)} />
          </div>
          <div>
            <label>Creditor BIC</label>
            <input className="input" value={creditorBic} onChange={e => setCreditorBic(e.target.value)} />
          </div>
          <div className="grid grid-3">
            <input className="input" value={amount} onChange={e => setAmount(e.target.value)} />
            <input className="input" value={currency} onChange={e => setCurrency(e.target.value.toUpperCase())} />
            <input className="input" value={reference} onChange={e => setReference(e.target.value)} />
          </div>
          <label><input type="checkbox" checked={dryRun} onChange={e => setDryRun(e.target.checked)} /> Dry run</label>
          <div>
            <button className="btn" onClick={createTransfer}>Submit</button>
          </div>
        </div>
      </section>
      <section className="card">
        <h2>Transfers</h2>
        {transfers.map(t => (
          <div key={t.id} className="card">
            <div>ID {t.id} — {t.status} — {t.reference}</div>
            <button className="btn" onClick={() => loadEvents(t.id)}>Load timeline</button>
            <ul>
              {(events[t.id]||[]).map(ev => <li key={ev.id}>{ev.type} — {ev.payload}</li>)}
            </ul>
          </div>
        ))}
      </section>
    </div>
  )
}