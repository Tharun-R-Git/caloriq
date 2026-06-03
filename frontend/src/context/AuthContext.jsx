import { createContext, useContext, useState, useEffect } from 'react'
import * as api from '../api/api'

const AuthContext = createContext(null)

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null)
  const [loading, setLoading] = useState(true)

  // On boot, if we have a token, validate it by fetching the current user.
  useEffect(() => {
    if (!api.getToken()) {
      setLoading(false)
      return
    }
    api.getMe()
      .then(setUser)
      .catch(() => {
        api.clearToken()
        setUser(null)
      })
      .finally(() => setLoading(false))
  }, [])

  const login = async (email, password) => {
    const res = await api.login(email, password)
    api.setToken(res.access_token)
    setUser(res.user)
    return res.user
  }

  const register = async (email, password, name) => {
    const res = await api.register(email, password, name)
    api.setToken(res.access_token)
    setUser(res.user)
    return res.user
  }

  const logout = () => {
    api.clearToken()
    setUser(null)
  }

  return (
    <AuthContext.Provider value={{ user, setUser, loading, login, register, logout }}>
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  const ctx = useContext(AuthContext)
  if (!ctx) throw new Error('useAuth must be used within AuthProvider')
  return ctx
}
