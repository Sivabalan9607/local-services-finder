import { useState, useEffect } from 'react'
import { useNavigate, Link } from 'react-router-dom'

const API = 'http://localhost:8000/api'

export default function AddService() {
  const [form, setForm] = useState({ name: '', category: '', phone: '', address: '', pincode: '' })
  const [file, setFile] = useState(null)
  const [loading, setLoading] = useState(false)
  const navigate = useNavigate()

  useEffect(() => {
    const token = localStorage.getItem('token')
    if (!token) navigate('/login')
  }, [navigate])

  const handleSubmit = (e) => {
    e.preventDefault()
    setLoading(true)
    const fd = new FormData()
    Object.entries(form).forEach(([k, v]) => fd.append(k, v))
    if (file) fd.append('image', file)
    const token = localStorage.getItem('token')

    fetch(`${API}/services`, { method: 'POST', headers: { Authorization: `Bearer ${token}` }, body: fd })
      .then(async r => {
        const d = await r.json()
        if (r.ok) navigate('/admin')
        else alert(d.detail || 'Failed')
      })
      .catch(() => alert('Failed'))
      .finally(() => setLoading(false))
  }

  return (
    <div className="form-page">
      <div className="form-box">
        <h2>Add New Service</h2>
        <form onSubmit={handleSubmit}>
          <input type="text" placeholder="Service Name" required value={form.name}
            onChange={e => setForm({ ...form, name: e.target.value })} />
          <input type="text" placeholder="Category (e.g. Plumber)" required value={form.category}
            onChange={e => setForm({ ...form, category: e.target.value })} />
          <input type="text" placeholder="Phone Number" required value={form.phone}
            onChange={e => setForm({ ...form, phone: e.target.value })} />
          <input type="text" placeholder="Address" required value={form.address}
            onChange={e => setForm({ ...form, address: e.target.value })} />
          <input type="text" placeholder="Pincode" required value={form.pincode}
            onChange={e => setForm({ ...form, pincode: e.target.value })} />
          <input type="file" accept="image/*" onChange={e => setFile(e.target.files[0])} />
          <button type="submit" disabled={loading}>{loading ? 'Saving...' : 'Add Service'}</button>
        </form>
        <div className="back-link"><Link to="/admin">Back to Admin</Link></div>
      </div>
    </div>
  )
}
