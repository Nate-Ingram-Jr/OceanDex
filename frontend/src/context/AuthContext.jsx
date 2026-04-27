import { createContext, useContext, useState } from 'react'

const AuthContext = createContext(null)

export function AuthProvider({ children }) {
  const [user, setUser] = useState(() => {
    try { return JSON.parse(localStorage.getItem('od_user')) } catch { return null }
  })

  function login(token, userData) {
    localStorage.setItem('od_token', token)
    localStorage.setItem('od_user', JSON.stringify(userData))
    setUser(userData)
  }

  function logout() {
    localStorage.removeItem('od_token')
    localStorage.removeItem('od_user')
    setUser(null)
  }

  return (
    <AuthContext.Provider value={{ user, login, logout }}>
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  return useContext(AuthContext)
}

export function authHeaders() {
  const token = localStorage.getItem('od_token')
  return token ? { Authorization: `Bearer ${token}` } : {}
}
