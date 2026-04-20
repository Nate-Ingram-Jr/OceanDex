import { NavLink } from 'react-router-dom'

export default function NavBar() {
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
      <div className="navbar-alert">
        <span className="alert-dot" />
        31% of sharks endangered
      </div>
    </nav>
  )
}
