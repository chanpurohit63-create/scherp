import React from 'react'
import { NavLink, useNavigate } from 'react-router-dom'
import { useAuth } from '../hooks/useAuth.jsx'
import NotificationBell from './NotificationBell'
import { useNotifications } from './NotificationProvider'
import ChildSwitcher from './ChildSwitcher'

const NAV_ITEMS = [
  { to: '/parent/dashboard', label: 'Dashboard', icon: '📊' },
  { to: '/parent/children', label: 'My Children', icon: '👨‍👩‍👧‍👦' },
  { to: '/parent/attendance', label: 'Attendance', icon: '📋' },
  { to: '/parent/homework', label: 'Homework', icon: '📝' },
  { to: '/parent/exams', label: 'Exam Results', icon: '🏆' },
  { to: '/parent/fees', label: 'Fee Payments', icon: '💰' },
  { to: '/parent/payment-history', label: 'Payment History', icon: '🧾' },
  { to: '/parent/certificates', label: 'Certificates', icon: '🎓' },
  { to: '/parent/documents', label: 'Documents', icon: '📄' },
  { to: '/parent/notices', label: 'School Notices', icon: '📢' },
  { to: '/parent/events', label: 'Events', icon: '📅' },
  { to: '/parent/messages', label: 'Messages', icon: '💬' },
  { to: '/parent/profile', label: 'Profile', icon: '👤' },
  { to: '/parent/change-password', label: 'Change Password', icon: '🔑' },
]

export default function ParentLayout({ title, children, hideChildSwitcher }) {
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
        <div className="sidebar-logo">
          <span style={{ fontSize: '1.2rem' }}>🏫</span> Parent Portal
        </div>
        <nav className="sidebar-nav">
          {NAV_ITEMS.map((item) => (
            <NavLink key={item.to} to={item.to} className={({ isActive }) => `sidebar-link ${isActive ? 'active' : ''}`} end={item.to === '/parent/dashboard'}>
              <span className="icon">{item.icon}</span>
              <span className="sidebar-label">{item.label}</span>
              {item.label === 'Messages' && unreadCount > 0 && (
                <span className="sidebar-badge">{unreadCount}</span>
              )}
            </NavLink>
          ))}
        </nav>
        <div className="sidebar-footer">
          <div className="sidebar-user">
            <span className="sidebar-user-avatar">👤</span>
            <span className="sidebar-user-name">{auth.profile?.full_name || auth.profile?.email}</span>
          </div>
          <button className="btn btn-sm btn-logout" onClick={handleLogout} style={{ width: '100%' }}>🚪 Logout</button>
        </div>
      </aside>
      <main className="main-content">
        <div className="main-content-header">
          <div className="main-content-header-left">
            <h1 style={{ margin: 0, fontSize: '1.5rem' }}>{title}</h1>
          </div>
          <div className="main-content-header-right">
            {!hideChildSwitcher && <ChildSwitcher />}
            <NotificationBell unreadCount={unreadCount} />
          </div>
        </div>
        {children}
      </main>
    </div>
  )
}