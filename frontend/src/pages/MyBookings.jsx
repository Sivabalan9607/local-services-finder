import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'

const API = 'http://localhost:8000/api'

export default function MyBookings() {
  const [bookings, setBookings] = useState([])

  useEffect(() => {
    const token = localStorage.getItem('token')
    fetch(`${API}/bookings`, { headers: { Authorization: `Bearer ${token}` } })
      .then(r => r.json())
      .then(setBookings)
      .catch(() => {})
  }, [])

  return (
    <div className="bookings-container">
      <h2>My Booked Services</h2>
      {bookings.length === 0 ? (
        <div className="empty-state">
          You have not booked any services yet.
          <br /><br />
          <Link to="/" className="btn btn-primary">Browse Services</Link>
        </div>
      ) : (
        <div className="bookings-grid">
          {bookings.map(b => (
            <div className="booking-card" key={b.id}>
              {b.service_image ? (
                <img src={`http://localhost:8000/uploads/${b.service_image}`} alt="" />
              ) : (
                <div style={{ width: '100%', height: 160, borderRadius: 12, background: 'rgba(255,255,255,0.05)', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: 48 }}>🛠️</div>
              )}
              <h3>{b.service_name}</h3>
              <p><strong>Category:</strong> {b.category}</p>
              <p><strong>Phone:</strong> {b.service_phone}</p>
              <p><strong>Address:</strong> {b.service_address}</p>
              <div className="booking-date">
                Booking Date: {b.booking_date}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
