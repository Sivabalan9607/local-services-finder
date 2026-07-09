export default function Footer() {
  return (
    <footer className="footer">
      <div className="footer-content">
        <div className="footer-col">
          <h4>Service Provider</h4>
          <p>Your trusted urban service partner.</p>
        </div>
        <div className="footer-col">
          <h4>Quick Links</h4>
          <a href="/">Home</a>
          <a href="/my-bookings">My Bookings</a>
          <a href="/admin">Admin</a>
        </div>
        <div className="footer-col">
          <h4>Contact</h4>
          <p>support@servicefinderpro.com</p>
          <p>+1 (555) 123-4567</p>
        </div>
      </div>
      <div className="footer-bottom">
        &copy; {new Date().getFullYear()} Service Finder Pro. All rights reserved.
      </div>
    </footer>
  )
}
