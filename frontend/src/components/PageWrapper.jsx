import React from 'react'
import { NavLink, useNavigate } from 'react-router-dom'
import { useAuth } from '../hooks/useAuth.jsx'
import NotificationBell from './NotificationBell'
import { useNotifications } from './NotificationProvider'

const NAV_ITEMS = [
  { to: '/dashboard', label: 'Dashboard', icon: '📊' },
  { to: '/users', label: 'Users', icon: '👥', adminOnly: true },
  { to: '/students', label: 'Students', icon: '👨‍🎓' },
  { to: '/teachers', label: 'Teachers', icon: '👩‍🏫' },
  { to: '/parents', label: 'Parents', icon: '👪' },
  { to: '/academic-years', label: 'Acad. Years', icon: '📅', adminOnly: true },
  { to: '/classes', label: 'Classes', icon: '🏫', adminOnly: true },
  { to: '/sections', label: 'Sections', icon: '📐', adminOnly: true },
  { to: '/subjects', label: 'Subjects', icon: '📚', adminOnly: true },
  { to: '/subject-allocations', label: 'Allocations', icon: '🔗', adminOnly: true },
  { to: '/enrollments', label: 'Enrollments', icon: '📋', adminOnly: true },
  { to: '/attendance', label: 'Attendance', icon: '📋' },
  { to: '/homework', label: 'Homework', icon: '📝' },
  { to: '/exams', label: 'Exams', icon: '📝' },
  { to: '/exam-results', label: 'Exam Results', icon: '📊' },
  { to: '/fees', label: 'Fees', icon: '💰' },
  { to: '/payments', label: 'Payments', icon: '💳' },
  { to: '/notices', label: 'Notices', icon: '📢' },
  { to: '/events', label: 'Events', icon: '🎉' },
  { to: '/certificates', label: 'Certificates', icon: '🎓' },
  { to: '/reports', label: 'Reports', icon: '📈' },
  { to: '/settings', label: 'Settings', icon: '⚙️' },
]

export default function PageWrapper({ title, children }) {
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
        <div className="sidebar-logo">School ERP</div>
        <nav className="sidebar-nav">
          {NAV_ITEMS.map((item) => {
            if (item.adminOnly && !auth.hasRole(['Super Admin', 'School Admin'])) return null
            return (
              <NavLink key={item.to} to={item.to} className={({ isActive }) => `sidebar-link ${isActive ? 'active' : ''}`}>
                <span className="icon">{item.icon}</span>
                <span>{item.label}</span>
              </NavLink>
            )
          })}
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
