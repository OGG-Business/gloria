import { useState } from 'react'
import axios from 'axios'

export default function TransferForm() {
  const [form, setForm] = useState({
    amount: 0,
    currency: 'USD',
    debtor_iban: '',
    debtor_bic: '',
    creditor_iban: '',
    creditor_bic: '',
    remittance_info: ''
  })
  const [resp, setResp] = useState<any>(null)
  const onChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setForm({...form, [e.target.name]: e.target.value})
  }
  const submit = async (e: React.FormEvent) => {
    e.preventDefault()
    const r = await axios.post('/transfers/', form)
    setResp(r.data)
  }
  return (
    <form onSubmit={submit} style={{display:'grid', gap:8, maxWidth: 600}}>
      <input name="amount" type="number" step="0.01" placeholder="Montant" onChange={onChange} required />
      <input name="currency" placeholder="Devise (ex: USD)" onChange={onChange} required />
      <input name="debtor_iban" placeholder="IBAN débiteur" onChange={onChange} required />
      <input name="debtor_bic" placeholder="BIC débiteur" onChange={onChange} required />
      <input name="creditor_iban" placeholder="IBAN créditeur" onChange={onChange} required />
      <input name="creditor_bic" placeholder="BIC créditeur" onChange={onChange} required />
      <input name="remittance_info" placeholder="Référence" onChange={onChange} />
      <button type="submit">Envoyer</button>
      {resp && <pre style={{background:'#f7f7f7', padding: 12}}>{JSON.stringify(resp, null, 2)}</pre>}
    </form>
  )
}