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
    <div style={{ maxWidth: 960, margin: '0 auto', padding: 16 }}>
      <h1>Global Payments Platform</h1>
      <section>
        <h2>Auth</h2>
        <input style={{ width: '100%' }} placeholder="Paste Bearer token (Keycloak)" value={token} onChange={e => setToken(e.target.value)} />
      </section>
      <section>
        <h2>Initiate transfer</h2>
        <div>
          <label>Debtor account</label>
          <select value={selectedAccount ?? ''} onChange={e => setSelectedAccount(parseInt(e.target.value))}>
            <option value="">Select</option>
            {accounts.map(a => <option key={a.id} value={a.id}>{a.display_name} - {a.iban}</option>)}
          </select>
        </div>
        <div>
          <label>Creditor IBAN</label>
          <input value={creditorIban} onChange={e => setCreditorIban(e.target.value)} />
        </div>
        <div>
          <label>Creditor BIC</label>
          <input value={creditorBic} onChange={e => setCreditorBic(e.target.value)} />
        </div>
        <div style={{ display: 'flex', gap: 8 }}>
          <input style={{ width: 120 }} value={amount} onChange={e => setAmount(e.target.value)} />
          <input style={{ width: 80 }} value={currency} onChange={e => setCurrency(e.target.value.toUpperCase())} />
          <input style={{ flex: 1 }} value={reference} onChange={e => setReference(e.target.value)} />
        </div>
        <label><input type="checkbox" checked={dryRun} onChange={e => setDryRun(e.target.checked)} /> Dry run</label>
        <div>
          <button onClick={createTransfer}>Submit</button>
        </div>
      </section>
      <section>
        <h2>Transfers</h2>
        {transfers.map(t => (
          <div key={t.id} style={{ border: '1px solid #ddd', padding: 8, marginBottom: 8 }}>
            <div>ID {t.id} — {t.status} — {t.reference}</div>
            <button onClick={() => loadEvents(t.id)}>Load timeline</button>
            <ul>
              {(events[t.id]||[]).map(ev => <li key={ev.id}>{ev.type} — {ev.payload}</li>)}
            </ul>
          </div>
        ))}
      </section>
    </div>
  )
}