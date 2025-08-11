import { useEffect, useState } from 'react'
import axios from 'axios'

export default function Dashboard() {
  const [health, setHealth] = useState('')
  useEffect(() => {
    axios.get('/health').then(r => setHealth(r.data.status)).catch(() => setHealth('unreachable'))
  }, [])
  return (
    <div>
      <h2>Dashboard</h2>
      <p>Backend: {health}</p>
    </div>
  )
}