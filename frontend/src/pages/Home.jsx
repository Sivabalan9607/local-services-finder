import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'

const API = 'http://localhost:8000/api'

const categoryIcons = {
  'Plumber': '🔧', 'Electrician': '⚡', 'Mechanic': '🔩',
  'AC Tech': '❄️', 'Cleaner': '🧹', 'Painter': '🎨',
  'Carpenter': '🪚', 'Mover': '📦',
}

const categoryColors = {
  'Plumber': '#2196F3', 'Electrician': '#FF9800', 'Mechanic': '#9C27B0',
  'AC Tech': '#00BCD4', 'Cleaner': '#4CAF50', 'Painter': '#E91E63',
  'Carpenter': '#795548', 'Mover': '#607D8B',
}

export default function Home() {
  const [services, setServices] = useState([])
  const [categories, setCategories] = useState([])
  const [category, setCategory] = useState('')
  const [pincode, setPincode] = useState('')
  const [user, setUser] = useState(null)
  const [bookDate, setBookDate] = useState({})
  const [reviews, setReviews] = useState({})
  const [reviewTexts, setReviewTexts] = useState({})
  const [reviewRatings, setReviewRatings] = useState({})

  useEffect(() => {
    const u = localStorage.getItem('user')
    if (u) setUser(JSON.parse(u))
    fetch(`${API}/categories`).then(r => r.json()).then(setCategories).catch(() => {})
    fetch(`${API}/services`).then(r => r.json()).then(setServices).catch(() => {})
  }, [])

  const search = () => {
    const params = new URLSearchParams()
    if (category) params.set('category', category)
    if (pincode) params.set('pincode', pincode)
    fetch(`${API}/services?${params}`).then(r => r.json()).then(setServices).catch(() => {})
  }

  const handleBook = (serviceId) => {
    if (!user) return alert('Please login to book')
    const date = bookDate[serviceId]
    if (!date) return alert('Select a booking date')
    const token = localStorage.getItem('token')
    fetch(`${API}/bookings`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${token}` },
      body: JSON.stringify({ service_id: serviceId, booking_date: date }),
    })
      .then(async r => {
        const d = await r.json()
        if (r.ok) { alert('Booked successfully!'); return }
        alert(d.detail || 'Booking failed')
      })
      .catch(() => alert('Booking failed'))
  }

  const submitReview = (serviceId) => {
    if (!user) return alert('Please login to review')
    const rating = reviewRatings[serviceId]
    const comment = reviewTexts[serviceId]
    if (!rating) return alert('Select a rating')
    const token = localStorage.getItem('token')
    fetch(`${API}/reviews`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${token}` },
      body: JSON.stringify({ service_id: serviceId, rating: Number(rating), comment: comment || '' }),
    })
      .then(async r => {
        const d = await r.json()
        if (r.ok) { alert('Review submitted!'); loadReviews(serviceId); return }
        alert(d.detail || 'Failed')
      })
      .catch(() => alert('Failed'))
  }

  const loadReviews = (serviceId) => {
    fetch(`${API}/reviews/${serviceId}`).then(r => r.json()).then(data => {
      setReviews(prev => ({ ...prev, [serviceId]: data }))
    }).catch(() => {})
  }

  useEffect(() => {
    services.forEach(s => loadReviews(s.id))
  }, [services])

  const getDefaultImg = (cat) => {
    const map = {
      'Plumber': 'https://images.unsplash.com/photo-1581578731548-c64695cc7162?w=400&h=250&fit=crop',
      'Electrician': 'https://images.unsplash.com/photo-1621905252507-b35492cc74b4?w=400&h=250&fit=crop',
      'Mechanic': 'https://images.unsplash.com/photo-1530046339160-ce3e530c7d2f?w=400&h=250&fit=crop',
      'AC Tech': 'https://images.unsplash.com/photo-1585771724684-38269d6639fd?w=400&h=250&fit=crop',
      'Cleaner': 'https://images.unsplash.com/photo-1584820927498-cfe5211fd8bf?w=400&h=250&fit=crop',
      'Painter': 'https://images.unsplash.com/photo-1562259929-b4e1fd3aef09?w=400&h=250&fit=crop',
      'Carpenter': 'https://images.unsplash.com/photo-1617529497471-92186319dccc?w=400&h=250&fit=crop',
    }
    return map[cat] || 'https://images.unsplash.com/photo-1581092160562-40aa08e78837?w=400&h=250&fit=crop'
  }

  return (
    <div className="home-container">
      <div className="hero">
        <h1>Service Finder Pro</h1>
        <p>Find trusted professionals near you in Chennai</p>
        <p className="tagline">🔧 Plumbing • ⚡ Electrical • 🔩 Mechanic • ❄️ AC • 🧹 Cleaning & more</p>
      </div>

      <div className="top-bar">
        {user ? (
          <span>Welcome, {user.username || user.full_name} 👋</span>
        ) : (
          <>
            <Link to="/login">Login</Link>
            <Link to="/register">Signup</Link>
          </>
        )}
      </div>

      <div className="search-bar">
        <select value={category} onChange={e => setCategory(e.target.value)}>
          <option value="">All Categories</option>
          {categories.map((c, i) => (
            <option key={i} value={c.name}>{categoryIcons[c.name] || '🛠'} {c.name}</option>
          ))}
        </select>
        <input type="text" placeholder="Search by pincode…" value={pincode}
          onChange={e => setPincode(e.target.value)} />
        <button onClick={search}>🔍 Search</button>
      </div>

      <div className="result-count">Showing {services.length} service{services.length !== 1 ? 's' : ''} in Chennai</div>

      {services.length === 0 ? (
        <div className="no-results">😕 No services found.</div>
      ) : (
        <div className="services-grid">
          {services.map(s => (
            <div className="service-card" key={s.id}>
              <div className="card-img-wrap">
                <img
                  src={s.image ? `http://localhost:8000/uploads/${s.image}` : getDefaultImg(s.category)}
                  alt={s.name}
                  loading="lazy"
                />
                <div className="card-img-overlay">
                  <span className="category-badge" style={{ background: `${categoryColors[s.category] || '#ff9800'}22`, color: categoryColors[s.category] || '#ff9800' }}>
                    {categoryIcons[s.category] || '🛠'} {s.category}
                  </span>
                </div>
              </div>

              <div className="card-body">
                <h3>{s.name}</h3>
                <div style={{ marginBottom: 6 }}>
                  {'⭐'.repeat(Math.round(s.rating || 0))}
                  {s.rating > 0 && <span style={{ fontSize: 12, color: 'rgba(255,255,255,0.4)', marginLeft: 4 }}>({s.rating})</span>}
                </div>
                <div className="details-grid">
                  <div><div className="label">Phone</div><div className="value">{s.phone}</div></div>
                  <div><div className="label">Pincode</div><div className="value">{s.pincode}</div></div>
                  <div style={{ gridColumn: '1 / -1' }}>
                    <div className="label">Address</div>
                    <div className="value">{s.address}</div>
                  </div>
                </div>
              </div>

              <div className="actions">
                <a href={`tel:${s.phone}`} className="btn btn-call">📞 Call</a>
                <a href={`https://wa.me/${s.phone}`} target="_blank" rel="noopener noreferrer" className="btn btn-wa">💬 WhatsApp</a>
                <a href={`https://www.google.com/maps/search/?api=1&query=${encodeURIComponent(s.address)}`} target="_blank" rel="noopener noreferrer" className="btn btn-map">📍 Map</a>
              </div>

              {user && (
                <div className="booking-row">
                  <input type="date" onChange={e => setBookDate({ ...bookDate, [s.id]: e.target.value })} />
                  <button className="btn-book" onClick={() => handleBook(s.id)}>Book Now</button>
                </div>
              )}

              <div className="reviews-section">
                <strong>⭐ Reviews</strong>
                {reviews[s.id] && reviews[s.id].length > 0 ? (
                  reviews[s.id].map(r => (
                    <div className="review-item" key={r.id}>
                      {'⭐'.repeat(r.rating)} {r.comment}
                      {r.username && <span style={{ opacity: 0.4, fontSize: 11, marginLeft: 6 }}>— {r.username}</span>}
                    </div>
                  ))
                ) : (
                  <div className="review-item" style={{ opacity: 0.5 }}>No reviews yet.</div>
                )}
                {user && (
                  <div className="review-form">
                    <select onChange={e => setReviewRatings({ ...reviewRatings, [s.id]: e.target.value })}>
                      <option value="">Rate this service…</option>
                      {[5,4,3,2,1].map(n => <option key={n} value={n}>{n} ⭐</option>)}
                    </select>
                    <textarea placeholder="Write your review…" rows={2}
                      onChange={e => setReviewTexts({ ...reviewTexts, [s.id]: e.target.value })} />
                    <button onClick={() => submitReview(s.id)}>Submit Review</button>
                  </div>
                )}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
