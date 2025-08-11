import { Outlet, Link } from 'react-router-dom'

export default function App() {
  return (
    <div>
      <nav style={{display: 'flex', gap: 12, padding: 12, borderBottom: '1px solid #eee'}}>
        <Link to="/">Dashboard</Link>
        <Link to="/new">Initier un transfert</Link>
        <Link to="/admin">Admin</Link>
      </nav>
      <main style={{padding: 16}}>
        <Outlet />
      </main>
    </div>
  )
}