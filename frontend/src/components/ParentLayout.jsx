import React from 'react'
import { NavLink, useNavigate } from 'react-router-dom'
import { useAuth } from '../hooks/useAuth.jsx'
import NotificationBell from './NotificationBell'
import { useNotifications } from './NotificationProvider'

const NAV_ITEMS = [
  { to: '/parent/dashboard', label: 'Dashboard', icon: '📊' },
  { to: '/parent/children', label: 'Children', icon: '👨‍👩‍👧‍👦' },
  { to: '/parent/notices', label: 'Notices', icon: '📢' },
  { to: '/parent/calendar', label: 'Calendar', icon: '📅' },
  { to: '/parent/messages', label: 'Messages', icon: '💬' },
  { to: '/parent/profile', label: 'Profile', icon: '👤' },
]

export default function ParentLayout({ title, children }) {
  const auth = useAuth()
  const navigate = useNavigate()
  const { unreadCount } = useNotifications()

  const handleLogout = () => {
    auth.logout()
    navigate('/login')
  }

  return (
    <div className="app-layout">
      <aside className="sidebar">
        <div className="sidebar-logo">Parent Portal</div>
        <nav className="sidebar-nav">
          {NAV_ITEMS.map((item) => (
            <NavLink key={item.to} to={item.to} className={({ isActive }) => `sidebar-link ${isActive ? 'active' : ''}`}>
              <span className="icon">{item.icon}</span>
              <span>{item.label}</span>
            </NavLink>
          ))}
        </nav>
        <div className="sidebar-footer">
          <div className="sidebar-user">{auth.profile?.full_name || auth.profile?.email}</div>
          <button className="btn btn-sm" onClick={handleLogout} style={{ width: '100%' }}>Logout</button>
        </div>
      </aside>
      <main className="main-content">
        <div className="main-content-header">
          <h1 style={{ margin: 0, fontSize: '1.5rem' }}>{title}</h1>
          <NotificationBell unreadCount={unreadCount} />
        </div>
        {children}
      </main>
    </div>
  )
}

