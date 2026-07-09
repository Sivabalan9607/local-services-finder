import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'

const API = (import.meta.env.VITE_API_URL || 'http://localhost:8000') + '/api'

export default function Admin() {
  const [services, setServices] = useState([])

  const load = () => {
    fetch(`${API}/services`).then(r => r.json()).then(setServices).catch(() => {})
  }

  useEffect(load, [])

  const del = (id) => {
    if (!confirm('Delete this service?')) return
    const token = localStorage.getItem('token')
    fetch(`${API}/services/${id}`, { method: 'DELETE', headers: { Authorization: `Bearer ${token}` } })
      .then(r => r.json()).then(() => load())
      .catch(() => alert('Delete failed'))
  }

  return (
    <div className="admin-container">
      <h2>Admin Dashboard</h2>
      <div className="top-actions">
        <Link to="/" className="btn btn-secondary">Back to Home</Link>
        <a href="/logout" className="btn btn-danger"
          onClick={e => { e.preventDefault(); localStorage.clear(); window.location.href = '/' }}>Logout</a>
        <Link to="/admin/add" className="btn btn-primary">Add Service</Link>
      </div>
      <div className="admin-card">
        <table className="admin-table">
          <thead>
            <tr>
              <th>Image</th>
              <th>Name</th>
              <th>Category</th>
              <th>Phone</th>
              <th>Pincode</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {services.map(s => (
              <tr key={s.id}>
                <td>
                  {s.image
                    ? <img src={`${import.meta.env.VITE_API_URL || 'http://localhost:8000'}/uploads/${s.image}`} alt="" />
                    : <div style={{ width: 50, height: 50, borderRadius: 8, background: 'rgba(255,255,255,0.1)', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>🛠️</div>
                  }
                </td>
                <td><strong>{s.name}</strong></td>
                <td>{s.category}</td>
                <td>{s.phone}</td>
                <td>{s.pincode}</td>
                <td style={{ display: 'flex', gap: 6, flexWrap: 'wrap' }}>
                  <Link to={`/admin/edit/${s.id}`} className="btn btn-secondary btn-sm">Edit</Link>
                  <button className="btn btn-danger btn-sm" onClick={() => del(s.id)}>Delete</button>
                </td>
              </tr>
            ))}
            {services.length === 0 && (
              <tr><td colSpan={6} style={{ textAlign: 'center', padding: 30, opacity: 0.6 }}>No services yet.</td></tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  )
}
