import { useState } from 'react'
import { Link } from 'react-router-dom'

const API = 'http://localhost:8000'

export default function Login() {
  const [form, setForm] = useState({ username: '', password: '' })
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  const handleSubmit = (e) => {
    e.preventDefault()
    setError('')
    setLoading(true)
    fetch(`${API}/auth/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(form),
    })
      .then(async r => {
        const data = await r.json()
        if (!r.ok) throw new Error(data.detail || 'Login failed')
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
        <h2>Login</h2>
        {error && <div className="error-msg">{error}</div>}
        <form onSubmit={handleSubmit}>
          <input type="text" placeholder="Username" required value={form.username}
            onChange={e => setForm({ ...form, username: e.target.value })} />
          <input type="password" placeholder="Password" required value={form.password}
            onChange={e => setForm({ ...form, password: e.target.value })} />
          <button type="submit" disabled={loading}>{loading ? 'Logging in...' : 'Login'}</button>
        </form>
        <p>Don't have account? <Link to="/register">Signup</Link></p>
      </div>
    </div>
  )
}
