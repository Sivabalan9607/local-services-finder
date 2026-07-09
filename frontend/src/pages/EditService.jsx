import { useState, useEffect } from 'react'
import { useParams, useNavigate, Link } from 'react-router-dom'

const API = (import.meta.env.VITE_API_URL || 'http://localhost:8000') + '/api'

export default function EditService() {
  const { id } = useParams()
  const [form, setForm] = useState({ name: '', category: '', phone: '', address: '', pincode: '' })
  const [image, setImage] = useState(null)
  const [currentImage, setCurrentImage] = useState('')
  const [loading, setLoading] = useState(false)
  const navigate = useNavigate()

  useEffect(() => {
    fetch(`${API}/services/${id}`)
      .then(r => r.json())
      .then(d => {
        setForm({ name: d.name, category: d.category, phone: d.phone, address: d.address, pincode: d.pincode })
        if (d.image) setCurrentImage(`${import.meta.env.VITE_API_URL || 'http://localhost:8000'}/uploads/${d.image}`)
      })
      .catch(() => navigate('/admin'))
  }, [id, navigate])

  const handleSubmit = (e) => {
    e.preventDefault()
    setLoading(true)
    const fd = new FormData()
    Object.entries(form).forEach(([k, v]) => fd.append(k, v))
    if (image) fd.append('image', image)

    fetch(`${API}/services/${id}`, { method: 'PUT', body: fd })
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
        <h2>Edit Service</h2>
        <form onSubmit={handleSubmit}>
          {currentImage && <img src={currentImage} className="current-img" alt="" />}
          <input type="file" accept="image/*" onChange={e => {
            setImage(e.target.files[0])
            setCurrentImage(URL.createObjectURL(e.target.files[0]))
          }} />
          <input type="text" placeholder="Service Name" required value={form.name}
            onChange={e => setForm({ ...form, name: e.target.value })} />
          <input type="text" placeholder="Category" required value={form.category}
            onChange={e => setForm({ ...form, category: e.target.value })} />
          <input type="text" placeholder="Phone Number" required value={form.phone}
            onChange={e => setForm({ ...form, phone: e.target.value })} />
          <input type="text" placeholder="Address" required value={form.address}
            onChange={e => setForm({ ...form, address: e.target.value })} />
          <input type="text" placeholder="Pincode" required value={form.pincode}
            onChange={e => setForm({ ...form, pincode: e.target.value })} />
          <button type="submit" disabled={loading}>{loading ? 'Updating...' : 'Update Service'}</button>
        </form>
        <div className="back-link"><Link to="/admin">Back to Admin</Link></div>
      </div>
    </div>
  )
}
