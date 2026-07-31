import React, { useState } from 'react'
import { NavLink, useLocation } from 'react-router-dom'
import { useAuth } from '../hooks/useAuth.jsx'
import NotificationBell from './NotificationBell'
import { useNotifications } from './NotificationProvider'
import ProfileMenu from './ProfileMenu'

const NAV_SECTIONS = [
  {
    label: 'Main',
    items: [
      { to: '/super-admin/dashboard', label: 'Dashboard', icon: '📊' },
      { to: '/super-admin/schools', label: 'Schools', icon: '🏫' },
      { to: '/super-admin/subscriptions', label: 'Subscriptions', icon: '💳' },
      { to: '/super-admin/payments', label: 'Payments', icon: '💰' },
    ],
  },
  {
    label: 'Management',
    items: [
      { to: '/super-admin/audit-logs', label: 'Audit Logs', icon: '📋' },
      { to: '/super-admin/settings', label: 'Settings', icon: '⚙️' },
    ],
  },
]

export default function SuperAdminLayout({ title, children, breadcrumbs }) {
  const auth = useAuth()
  const location = useLocation()
  const { unreadCount } = useNotifications()
  const [darkMode, setDarkMode] = useState(() => localStorage.getItem('theme') === 'dark')

  const toggleTheme = () => {
    const newTheme = darkMode ? 'light' : 'dark'
    setDarkMode(!darkMode)
    localStorage.setItem('theme', newTheme)
    document.documentElement.setAttribute('data-theme', newTheme)
  }

  const getInitials = (name) => {
    if (!name) return 'SA'
    return name.split(' ').map(n => n[0]).join('').toUpperCase().slice(0, 2)
  }

  return (
    <div className="app-layout">
      <aside className="sidebar">
        <div className="sidebar-logo">
          <div className="logo-icon">⚡</div>
          <span className="logo-text">Super Admin</span>
        </div>
        {NAV_SECTIONS.map((section) => (
          <div key={section.label}>
            <div className="sidebar-section-label">{section.label}</div>
            <nav className="sidebar-nav">
              {section.items.map((item) => {
                const isActive = location.pathname === item.to || location.pathname.startsWith(item.to + '/')
                return (
                  <NavLink
                    key={item.to}
                    to={item.to}
                    className={`sidebar-link ${isActive ? 'active' : ''}`}
                    end={item.to === '/super-admin/dashboard'}
                  >
                    <span className="icon">{item.icon}</span>
                    <span className="sidebar-label">{item.label}</span>
                  </NavLink>
                )
              })}
            </nav>
          </div>
        ))}
        <div className="sidebar-footer">
          <div className="sidebar-user">
            <div className="sidebar-user-avatar">
              {getInitials(auth.profile?.full_name)}
            </div>
            <div className="sidebar-user-info">
              <div className="sidebar-user-name">{auth.profile?.full_name || auth.profile?.email}</div>
              <div className="sidebar-user-role">Super Admin</div>
            </div>
          </div>
        </div>
      </aside>
      <main className="main-content">
        <div className="main-content-header">
          <div className="main-content-header-left">
            {breadcrumbs && (
              <div className="breadcrumbs">
                {breadcrumbs.map((crumb, i) => (
                  <React.Fragment key={i}>
                    {i > 0 && <span className="separator">/</span>}
                    {crumb.to ? <a href={crumb.to}>{crumb.label}</a> : <span className="current">{crumb.label}</span>}
                  </React.Fragment>
                ))}
              </div>
            )}
            <h1 style={{ margin: 0, fontSize: '1.35rem', fontWeight: 700 }}>{title}</h1>
          </div>
          <div className="main-content-header-right">
            <button className="theme-toggle" onClick={toggleTheme} title={darkMode ? 'Switch to light mode' : 'Switch to dark mode'}>
              {darkMode ? '☀️ Light' : '🌙 Dark'}
            </button>
            <NotificationBell unreadCount={unreadCount} />
            <ProfileMenu />
          </div>
        </div>
        <div className="main-content-body">
          {children}
        </div>
      </main>
    </div>
  )
}
</arg_value>
</write_to_file></tool_call>