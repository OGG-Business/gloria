import React, { useEffect, useState } from 'react'
import { api, eventStreamUrl } from './api'

function AccountForm() {
  const [name, setName] = useState('')
  const [iban, setIban] = useState('')
  const [bic, setBic] = useState('')
  const [userId, setUserId] = useState('demo-user')
  const [accounts, setAccounts] = useState<any[]>([])

  async function load() {
    const data = await api<any[]>('/accounts')
    setAccounts(data)
  }
  useEffect(() => { load() }, [])

  async function submit(e: React.FormEvent) {
    e.preventDefault()
    await api('/accounts', { method: 'POST', body: JSON.stringify({ name, iban, bic, user_id: userId }) })
    setName(''); setIban(''); setBic('')
    await load()
  }

  return (
    <div>
      <h2>Comptes</h2>
      <form onSubmit={submit} style={{display:'grid', gap:8, maxWidth:420}}>
        <input placeholder='User ID' value={userId} onChange={e=>setUserId(e.target.value)} />
        <input placeholder='Nom du compte' value={name} onChange={e=>setName(e.target.value)} />
        <input placeholder='IBAN' value={iban} onChange={e=>setIban(e.target.value)} />
        <input placeholder='BIC (optionnel)' value={bic} onChange={e=>setBic(e.target.value)} />
        <button type='submit'>Créer</button>
      </form>
      <ul>
        {accounts.map(a => <li key={a.id}>{a.name} — {a.iban}</li>)}
      </ul>
    </div>
  )
}

function TransferForm() {
  const [accounts, setAccounts] = useState<any[]>([])
  const [debtor, setDebtor] = useState<number|undefined>()
  const [creditorName, setCreditorName] = useState('')
  const [creditorIban, setCreditorIban] = useState('')
  const [amount, setAmount] = useState('100.00')
  const [currency, setCurrency] = useState('USD')
  const [transfer, setTransfer] = useState<any|null>(null)
  const [events, setEvents] = useState<any[]>([])

  useEffect(() => { api<any[]>('/accounts').then(setAccounts) }, [])

  async function submit(e: React.FormEvent) {
    e.preventDefault()
    const tr = await api<any>('/transfers', { method: 'POST', body: JSON.stringify({ debtor_account_id: debtor, creditor_name: creditorName, creditor_iban: creditorIban, amount: parseFloat(amount), currency }) })
    setTransfer(tr)
    const es = new EventSource(eventStreamUrl(tr.id))
    es.onmessage = (msg) => {
      try { setEvents(prev => [...prev, JSON.parse(msg.data)]) } catch {}
    }
  }

  return (
    <div>
      <h2>Nouveau virement</h2>
      <form onSubmit={submit} style={{display:'grid', gap:8, maxWidth:420}}>
        <select onChange={e=>setDebtor(parseInt(e.target.value))} defaultValue="">
          <option value="" disabled>Compte débiteur</option>
          {accounts.map(a => <option key={a.id} value={a.id}>{a.name} — {a.iban}</option>)}
        </select>
        <input placeholder='Bénéficiaire' value={creditorName} onChange={e=>setCreditorName(e.target.value)} />
        <input placeholder='IBAN bénéficiaire' value={creditorIban} onChange={e=>setCreditorIban(e.target.value)} />
        <input placeholder='Montant' value={amount} onChange={e=>setAmount(e.target.value)} />
        <input placeholder='Devise (USD, EUR, ...)' value={currency} onChange={e=>setCurrency(e.target.value)} />
        <button type='submit'>Initier</button>
      </form>
      {transfer && (
        <div>
          <h3>Statut: {transfer.status}</h3>
          <ul>
            {events.map((ev, idx) => <li key={idx}>{ev.type} — {ev.at}</li>)}
          </ul>
        </div>
      )}
    </div>
  )
}

function Admin() {
  const [logs, setLogs] = useState<any[]>([])
  useEffect(() => { api<any[]>('/admin/logs').then(setLogs) }, [])
  return (
    <div>
      <h2>Admin</h2>
      <ul>
        {logs.map(l => <li key={l.id}>{l.created_at} — {l.action} — {l.entity}#{l.entity_id}</li>)}
      </ul>
    </div>
  )
}

export default function App() {
  const [tab, setTab] = useState<'comptes'|'virements'|'admin'>('comptes')
  return (
    <div style={{padding:16, fontFamily:'system-ui, sans-serif'}}>
      <h1>Open Payments Hub</h1>
      <nav style={{display:'flex', gap:8, marginBottom:16}}>
        <button onClick={()=>setTab('comptes')}>Comptes</button>
        <button onClick={()=>setTab('virements')}>Virements</button>
        <button onClick={()=>setTab('admin')}>Admin</button>
      </nav>
      {tab==='comptes' && <AccountForm />}
      {tab==='virements' && <TransferForm />}
      {tab==='admin' && <Admin />}
    </div>
  )
}