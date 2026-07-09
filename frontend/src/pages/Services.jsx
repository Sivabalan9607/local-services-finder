import { useState, useEffect } from 'react'
import ServiceCard from '../components/ServiceCard'

const API = (import.meta.env.VITE_API_URL || 'http://localhost:8000') + '/api'

export default function Services() {
  const [services, setServices] = useState([])
  const [categories, setCategories] = useState([])
  const [categoryFilter, setCategoryFilter] = useState('')
  const [cityFilter, setCityFilter] = useState('')

  useEffect(() => {
    fetch(`${API}/categories`)
      .then(r => r.json())
      .then(setCategories)
      .catch(() => {})

    fetch(`${API}/services`)
      .then(r => r.json())
      .then(setServices)
      .catch(() => {})
  }, [])

  const filtered = services.filter(s => {
    if (categoryFilter && s.category_id !== Number(categoryFilter)) return false
    if (cityFilter && !s.city?.toLowerCase().includes(cityFilter.toLowerCase())) return false
    return true
  })

  return (
    <>
      <div className="page-header">
        <h1>Our Services</h1>
        <p>Find the right professional for your needs</p>
      </div>

      <div className="services-page">
        <div className="filters">
          <select value={categoryFilter} onChange={e => setCategoryFilter(e.target.value)}>
            <option value="">All Categories</option>
            {categories.map(c => (
              <option key={c.id} value={c.id}>{c.name}</option>
            ))}
          </select>
          <input
            type="text"
            placeholder="Search by city..."
            value={cityFilter}
            onChange={e => setCityFilter(e.target.value)}
          />
        </div>

        <div className="service-list">
          {filtered.length === 0 ? (
            <p style={{ gridColumn: '1 / -1', textAlign: 'center', color: '#999', padding: 40 }}>
              {services.length === 0
                ? 'No services available yet. Please check back later.'
                : 'No services match your filters.'}
            </p>
          ) : (
            filtered.map(s => <ServiceCard key={s.id} service={s} />)
          )}
        </div>
      </div>
    </>
  )
}
