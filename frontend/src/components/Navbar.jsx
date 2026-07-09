import { Link, useNavigate } from 'react-router-dom'
import { useState, useEffect } from 'react'
import Logo from './Logo'

export default function Navbar() {
  const [user, setUser] = useState(null)
  const navigate = useNavigate()

  useEffect(() => {
    const u = localStorage.getItem('user')
    if (u) setUser(JSON.parse(u))
  }, [])

  const logout = () => {
    localStorage.removeItem('token')
    localStorage.removeItem('user')
    setUser(null)
    navigate('/')
  }

  return (
    <nav className="navbar">
      <Link to="/" className="logo-link"><Logo /></Link>
      <ul className="nav-links">
        <li><Link to="/">Home</Link></li>
        {user ? (
          <>
            <li><Link to="/my-bookings">My Bookings</Link></li>
            <li><span>Welcome, {user.username || user.full_name}</span></li>
            {user.role === 'admin' && <li><Link to="/admin">Admin</Link></li>}
            <li><a onClick={logout}>Logout</a></li>
          </>
        ) : (
          <>
            <li><Link to="/login">Login</Link></li>
            <li><Link to="/register" className="btn btn-primary">Signup</Link></li>
          </>
        )}
      </ul>
    </nav>
  )
}
