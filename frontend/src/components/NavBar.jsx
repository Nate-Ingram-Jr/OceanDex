import { NavLink, useNavigate } from 'react-router-dom'
import { useState, useEffect } from 'react'
import { useAuth } from '../context/AuthContext'

export default function NavBar() {
  const [facts, setFacts] = useState([])
  const [index, setIndex] = useState(0)
  const { user, logout } = useAuth()
  const navigate = useNavigate()

  useEffect(() => {
    fetch('/api/conservation-facts')
      .then(r => r.json())
      .then(setFacts)
      .catch(() => {})
  }, [])

  useEffect(() => {
    if (facts.length < 30) return
    const id = setInterval(() => setIndex(i => (i + 1) % facts.length), 30000)
    return () => clearInterval(id)
  }, [facts])

  return (
    <nav className="navbar">
      <div className="navbar-main">
        <div className="navbar-brand">
          <NavLink to="/" className="navbar-logo">OceanDex</NavLink>
          <span className="navbar-subtitle">Sea Life Encyclopedia</span>
        </div>

        <div className="navbar-links">
          <NavLink to="/" end className={({ isActive }) => 'nav-link' + (isActive ? ' active' : '')}>
            Explore
          </NavLink>
          <NavLink to="/ocean-map" className={({ isActive }) => 'nav-link' + (isActive ? ' active' : '')}>
            Ocean Map
          </NavLink>
          <NavLink to="/protected" className={({ isActive }) => 'nav-link' + (isActive ? ' active' : '')}>
            Protected
          </NavLink>
          <NavLink to="/id-scanner" className={({ isActive }) => 'nav-link' + (isActive ? ' active' : '')}>
            ID Scanner
          </NavLink>
          {user && (
            <NavLink to="/submit" className={({ isActive }) => 'nav-link nav-link-accent' + (isActive ? ' active' : '')}>
              + Submit
            </NavLink>
          )}
          {user?.role === 'admin' && (
            <NavLink to="/admin" className={({ isActive }) => 'nav-link nav-link-admin' + (isActive ? ' active' : '')}>
              Admin
            </NavLink>
          )}
        </div>

        <div className="navbar-user">
          {user ? (
            <>
              <span className="nav-username">{user.username}</span>
              <button className="nav-logout" onClick={() => { logout(); navigate('/') }}>Sign out</button>
            </>
          ) : (
            <button className="nav-logout" onClick={() => navigate('/login')}>Sign in</button>
          )}
        </div>
      </div>

      {facts.length > 0 && (
        <div className={`navbar-ticker ${facts[index].sentiment}`}>
          <span className="alert-dot" />
          <span className="ticker-text">{facts[index].text}</span>
        </div>
      )}
    </nav>
  )
}
