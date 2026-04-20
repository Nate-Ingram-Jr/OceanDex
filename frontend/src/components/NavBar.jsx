import { NavLink } from 'react-router-dom'
import { useState, useEffect } from 'react'

export default function NavBar() {
  const [facts, setFacts] = useState([])
  const [index, setIndex] = useState(0)

  useEffect(() => {
    fetch('http://localhost:8000/conservation-facts')
      .then(r => r.json())
      .then(setFacts)
      .catch(() => {})
  }, [])

  useEffect(() => {
    if (facts.length < 30) return
    const id = setInterval(() => setIndex(i => (i + 1) % facts.length), 4000)
    return () => clearInterval(id)
  }, [facts])

  return (
    <nav className="navbar">
      <div className="navbar-brand">
        <NavLink to="/" className="navbar-logo">OceanDex</NavLink>
        <span className="navbar-subtitle">/ Sea Life Encyclopedia</span>
      </div>
      <div className="navbar-links">
        <NavLink to="/" end className={({ isActive }) => 'nav-link' + (isActive ? ' active' : '')}>
          Explore
        </NavLink>
        <NavLink to="/ocean-map" className={({ isActive }) => 'nav-link' + (isActive ? ' active' : '')}>
          Ocean Map
        </NavLink>
        <NavLink to="/protected" className={({ isActive }) => 'nav-link' + (isActive ? ' active' : '')}>
          Protected List
        </NavLink>
        <NavLink to="/id-scanner" className={({ isActive }) => 'nav-link' + (isActive ? ' active' : '')}>
          ID Scanner
        </NavLink>
      </div>
      {facts.length > 0 && (
        <div className={`navbar-alert ${facts[index].sentiment}`}>
          <span className="alert-dot" />
          {facts[index].text}
        </div>
      )}
    </nav>
  )
}
