import { Link } from 'react-router-dom'

export default function ServiceCard({ service }) {
  return (
    <div className="service-item">
      <h3>{service.title}</h3>
      <p>{service.description}</p>
      <div className="price">${parseFloat(service.price).toFixed(2)}</div>
      <div className="city">{service.city}</div>
      <Link to="/login" className="btn btn-primary book-btn">Book Now</Link>
    </div>
  )
}
