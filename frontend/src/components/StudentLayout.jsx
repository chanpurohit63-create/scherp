import React from 'react'
import { NavLink, useNavigate, useLocation } from 'react-router-dom'
import { useAuth } from '../hooks/useAuth.jsx'
import NotificationBell from './NotificationBell'
import { useNotifications } from './NotificationProvider'

const NAV_ITEMS = [
  { to: '/student/dashboard', label: 'Dashboard', icon: '📊' },
  { to: '/student/profile', label: 'Profile', icon: '👤' },
  { to: '/student/attendance', label: 'Attendance', icon: '📋' },
  { to: '/student/homework', label: 'Homework', icon: '📝' },
  { to: '/student/exams', label: 'Exams', icon: '📝' },
  { to: '/student/fees', label: 'Fees', icon: '💰' },
  { to: '/student/notices', label: 'Notices', icon: '📢' },
  { to: '/student/calendar', label: 'Calendar', icon: '📅' },
  { to: '/student/documents', label: 'Documents', icon: '📄' },
  { to: '/student/messages', label: 'Messages', icon: '💬' },
]

export default function StudentLayout({ title, children, breadcrumbs }) {
  const auth = useAuth()
  const navigate = useNavigate()
  const location = useLocation()
  const { unreadCount } = useNotifications()

  const handleLogout = () => {
    auth.logout()
    navigate('/login')
  }

  const getInitials = (name) => {
    if (!name) return 'S'
    return name.split(' ').map(n => n[0]).join('').toUpperCase().slice(0, 2)
  }

  return (
    <div className="app-layout">
      <aside className="sidebar">
        <div className="sidebar-logo">
          <div className="logo-icon">🎓</div>
          <span className="logo-text">Student Portal</span>
        </div>
        <div className="sidebar-section-label">Navigation</div>
        <nav className="sidebar-nav">
          {NAV_ITEMS.map((item) => {
            const isActive = location.pathname === item.to || location.pathname.startsWith(item.to + '/')
            return (
              <NavLink
                key={item.to}
                to={item.to}
                className={`sidebar-link ${isActive ? 'active' : ''}`}
                end={item.to === '/student/dashboard'}
              >
                <span className="icon">{item.icon}</span>
                <span className="sidebar-label">{item.label}</span>
                {item.label === 'Messages' && unreadCount > 0 && (
                  <span className="sidebar-badge">{unreadCount}</span>
                )}
              </NavLink>
            )
          })}
        </nav>
        <div className="sidebar-footer">
          <div className="sidebar-user">
            <div className="sidebar-user-avatar">
              {getInitials(auth.profile?.full_name)}
            </div>
            <div className="sidebar-user-info">
              <div className="sidebar-user-name">{auth.profile?.full_name || auth.profile?.email}</div>
              <div className="sidebar-user-role">Student</div>
            </div>
          </div>
          <button className="btn-logout" onClick={handleLogout}>
            <span>🚪</span>
            <span>Logout</span>
          </button>
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
            <NotificationBell unreadCount={unreadCount} />
          </div>
        </div>
        <div className="main-content-body">
          {children}
        </div>
      </main>
    </div>
  )
}