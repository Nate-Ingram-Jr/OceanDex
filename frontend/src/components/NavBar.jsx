import { NavLink, useNavigate } from 'react-router-dom'
import { useState, useEffect } from 'react'
import { useAuth } from '../context/AuthContext'
import OceanDexLogo from './OceanDexLogo'

export default function NavBar() {
  const [facts, setFacts] = useState([])
  const [index, setIndex] = useState(0)
  const [menuOpen, setMenuOpen] = useState(false)
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

  // Close drawer when navigating
  const close = () => setMenuOpen(false)

  return (
    <nav className="navbar">
      <div className="navbar-main">
        <div className="navbar-brand">
          <div className="navbar-brand-icon" aria-hidden="true">
            <OceanDexLogo size={32} animated={true} showLabels={false} showLegend={false} />
          </div>
          <NavLink to="/" className="navbar-logo" onClick={close}>OceanDex</NavLink>
          <span className="navbar-subtitle">Sea Life Encyclopedia</span>
        </div>

        <div className={`navbar-links ${menuOpen ? 'open' : ''}`}>
          <NavLink to="/" end onClick={close} className={({ isActive }) => 'nav-link' + (isActive ? ' active' : '')}>
            Explore
          </NavLink>
          <NavLink to="/ocean-map" onClick={close} className={({ isActive }) => 'nav-link' + (isActive ? ' active' : '')}>
            Ocean Map
          </NavLink>
          <NavLink to="/protected" onClick={close} className={({ isActive }) => 'nav-link' + (isActive ? ' active' : '')}>
            Protected
          </NavLink>
          <NavLink to="/id-scanner" onClick={close} className={({ isActive }) => 'nav-link' + (isActive ? ' active' : '')}>
            ID Scanner
          </NavLink>
          <NavLink to="/sightings" onClick={close} className={({ isActive }) => 'nav-link' + (isActive ? ' active' : '')}>
            Sightings
          </NavLink>
          {user && (
            <NavLink to="/submit" onClick={close} className={({ isActive }) => 'nav-link nav-link-accent' + (isActive ? ' active' : '')}>
              + Submit
            </NavLink>
          )}
          {user?.role === 'admin' && (
            <NavLink to="/admin" onClick={close} className={({ isActive }) => 'nav-link nav-link-admin' + (isActive ? ' active' : '')}>
              Admin
            </NavLink>
          )}
          {/* User actions inside drawer on mobile */}
          <div className="navbar-drawer-user">
            {user ? (
              <>
                <NavLink to="/settings" onClick={close} className="nav-link">Settings</NavLink>
                <button className="nav-logout nav-link-btn" onClick={() => { logout(); navigate('/'); close() }}>
                  Sign out
                </button>
              </>
            ) : (
              <button className="nav-logout nav-link-btn" onClick={() => { navigate('/login'); close() }}>
                Sign in
              </button>
            )}
          </div>
        </div>

        <div className="navbar-user">
          {user ? (
            <>
              <NavLink to="/settings" className="nav-username">{user.username}</NavLink>
              <button className="nav-logout" onClick={() => { logout(); navigate('/') }}>Sign out</button>
            </>
          ) : (
            <button className="nav-logout" onClick={() => navigate('/login')}>Sign in</button>
          )}
        </div>

        <button
          className="navbar-hamburger"
          onClick={() => setMenuOpen(o => !o)}
          aria-label="Toggle menu"
        >
          <span className={`hamburger-line ${menuOpen ? 'open-top' : ''}`} />
          <span className={`hamburger-line ${menuOpen ? 'open-mid' : ''}`} />
          <span className={`hamburger-line ${menuOpen ? 'open-bot' : ''}`} />
        </button>
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
