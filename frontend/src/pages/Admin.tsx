import { useEffect, useState } from 'react'
import axios from 'axios'

export default function Admin() {
  const [audit, setAudit] = useState<any[]>([])
  useEffect(() => {
    axios.get('/admin/audit').then(r => setAudit(r.data)).catch(() => setAudit([]))
  }, [])
  return (
    <div>
      <h2>Admin</h2>
      <pre style={{background:'#f7f7f7', padding: 12, overflow:'auto'}}>{JSON.stringify(audit, null, 2)}</pre>
    </div>
  )
}