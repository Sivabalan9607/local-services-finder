import { useState } from 'react'
import { Link } from 'react-router-dom'

const API = import.meta.env.VITE_API_URL || 'http://localhost:8000'

export default function Register() {
  const [form, setForm] = useState({ username: '', full_name: '', phone: '', password: '', role: 'customer' })
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  const handleSubmit = (e) => {
    e.preventDefault()
    setError('')
    setLoading(true)
    fetch(`${API}/auth/register`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(form),
    })
      .then(async r => {
        const data = await r.json()
        if (!r.ok) throw new Error(data.detail || 'Registration failed')
        return data
      })
      .then(data => {
        localStorage.setItem('token', data.access_token)
        localStorage.setItem('user', JSON.stringify(data.user))
        window.location.href = '/'
      })
      .catch(err => setError(err.message))
      .finally(() => setLoading(false))
  }

  return (
    <div className="auth-page">
      <div className="auth-box">
        <h2>Signup</h2>
        {error && <div className="error-msg">{error}</div>}
        <form onSubmit={handleSubmit}>
          <input type="text" placeholder="Username" required value={form.username}
            onChange={e => setForm({ ...form, username: e.target.value })} />
          <input type="text" placeholder="Full Name" value={form.full_name}
            onChange={e => setForm({ ...form, full_name: e.target.value })} />
          <input type="tel" placeholder="Phone" value={form.phone}
            onChange={e => setForm({ ...form, phone: e.target.value })} />
          <input type="password" placeholder="Password" required value={form.password}
            onChange={e => setForm({ ...form, password: e.target.value })} />
          <button type="submit" disabled={loading}>{loading ? 'Creating account...' : 'Signup'}</button>
        </form>
        <p>Already have account? <Link to="/login">Login</Link></p>
      </div>
    </div>
  )
}
