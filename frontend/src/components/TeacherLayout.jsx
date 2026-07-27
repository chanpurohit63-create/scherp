import React from 'react'
import { NavLink, useNavigate } from 'react-router-dom'
import { useAuth } from '../hooks/useAuth.jsx'

const NAV_ITEMS = [
  { to: '/teacher/dashboard', label: 'Dashboard', icon: '📊' },
  { to: '/teacher/classes', label: 'My Classes', icon: '🏫' },
  { to: '/teacher/attendance', label: 'Attendance', icon: '📋' },
  { to: '/teacher/homework', label: 'Homework', icon: '📝' },
  { to: '/teacher/exams', label: 'Exams', icon: '📝' },
  { to: '/teacher/students', label: 'Students', icon: '👨‍🎓' },
  { to: '/teacher/notices', label: 'Notices', icon: '📢' },
  { to: '/teacher/calendar', label: 'Calendar', icon: '📅' },
  { to: '/teacher/messages', label: 'Messages', icon: '💬' },
  { to: '/teacher/profile', label: 'Profile', icon: '👤' },
]

export default function TeacherLayout({ title, children }) {
  const auth = useAuth()
  const navigate = useNavigate()

  const handleLogout = () => {
    auth.logout()
    navigate('/login')
  }

  return (
    <div className="app-layout">
      <aside className="sidebar">
        <div className="sidebar-logo">Teacher Portal</div>
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
        <h1 style={{ marginBottom: 24, fontSize: '1.5rem' }}>{title}</h1>
        {children}
      </main>
    </div>
  )
}

