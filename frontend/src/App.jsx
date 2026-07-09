import { Routes, Route } from 'react-router-dom'
import Navbar from './components/Navbar'
import Footer from './components/Footer'
import Home from './pages/Home'
import Login from './pages/Login'
import Register from './pages/Register'
import Admin from './pages/Admin'
import AddService from './pages/AddService'
import EditService from './pages/EditService'
import MyBookings from './pages/MyBookings'

export default function App() {
  return (
    <div className="app">
      <Navbar />
      <main className="main-content">
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/login" element={<Login />} />
          <Route path="/register" element={<Register />} />
          <Route path="/admin" element={<Admin />} />
          <Route path="/admin/add" element={<AddService />} />
          <Route path="/admin/edit/:id" element={<EditService />} />
          <Route path="/my-bookings" element={<MyBookings />} />
        </Routes>
      </main>
      <Footer />
    </div>
  )
}
