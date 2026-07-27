import React, { createContext, useContext, useEffect, useMemo, useState } from 'react'
import { fetchProfile } from '../api'

const ACCESS_TOKEN_KEY = 'school-erp-token'
const PROFILE_KEY = 'school-erp-profile'
const AuthContext = createContext(null)

export function AuthProvider({ children }) {
  const [token, setToken] = useState(() => localStorage.getItem(ACCESS_TOKEN_KEY) || '')
  const [profile, setProfile] = useState(() => {
    const raw = localStorage.getItem(PROFILE_KEY)
    return raw ? JSON.parse(raw) : null
  })

  useEffect(() => {
    if (token) {
      localStorage.setItem(ACCESS_TOKEN_KEY, token)
    } else {
      localStorage.removeItem(ACCESS_TOKEN_KEY)
    }
  }, [token])

  useEffect(() => {
    if (profile) {
      localStorage.setItem(PROFILE_KEY, JSON.stringify(profile))
    } else {
      localStorage.removeItem(PROFILE_KEY)
    }
  }, [profile])

  useEffect(() => {
    if (token && !profile) {
      fetchProfile(token)
        .then(setProfile)
        .catch(() => {
          setToken('')
          setProfile(null)
        })
    }
  }, [token, profile])

  const login = (newToken) => {
    setToken(newToken)
  }

  const logout = () => {
    setToken('')
    setProfile(null)
  }

  const value = useMemo(
    () => ({
      token,
      profile,
      login,
      logout,
      setProfile,
      isAuthenticated: Boolean(token),
      hasRole: (allowedRoles) => profile && allowedRoles.includes(profile.role),
    }),
    [token, profile]
  )

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}

export function useAuth() {
  const context = useContext(AuthContext)
  if (!context) {
    throw new Error('useAuth must be used within AuthProvider')
  }
  return context
}
