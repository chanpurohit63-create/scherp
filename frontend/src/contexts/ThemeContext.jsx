import React, { createContext, useContext, useState, useEffect } from 'react'
import toast, { Toaster } from 'react-hot-toast'

const ThemeContext = createContext()

export function ThemeProvider({ children }) {
  const [isDarkMode, setIsDarkMode] = useState(() => {
    const saved = localStorage.getItem('theme')
    if (saved === 'dark') return true
    if (saved === 'light') return false
    return window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches
  })

  const [primaryColor, setPrimaryColor] = useState(() => {
    return localStorage.getItem('theme-color') || '#4f46e5'
  })

  useEffect(() => {
    const root = document.documentElement
    if (isDarkMode) {
      root.setAttribute('data-theme', 'dark')
      localStorage.setItem('theme', 'dark')
    } else {
      root.setAttribute('data-theme', 'light')
      localStorage.setItem('theme', 'light')
    }
    root.style.setProperty('--primary-color', primaryColor)
    if (localStorage.getItem('theme-color') !== primaryColor) {
      localStorage.setItem('theme-color', primaryColor)
    }
  }, [isDarkMode, primaryColor])

  const toggleDarkMode = () => setIsDarkMode(!isDarkMode)

  const value = {
    isDarkMode,
    toggleDarkMode,
    primaryColor,
    setPrimaryColor,
  }

  return (
    <ThemeContext.Provider value={value}>
      {children}
    </ThemeContext.Provider>
  )
}

export const useTheme = () => {
  const context = useContext(ThemeContext)
  if (!context) throw new Error('useTheme must be used within ThemeProvider')
  return context
}

export const showToast = {
  success: (message) => toast.success(message, { position: 'top-right', duration: 3000 }),
  error: (message) => toast.error(message, { position: 'top-right', duration: 5000 }),
  info: (message) => toast.info(message, { position: 'top-right', duration: 4000 }),
  warning: (message) => toast.warning(message, { position: 'top-right', duration: 4000 }),
  loading: (message) => toast.loading(message, { position: 'top-right' }),
  dismiss: (id) => toast.dismiss(id),
}
