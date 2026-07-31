import React, { useState, useRef, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../hooks/useAuth.jsx'

export default function ProfileMenu() {
  const auth = useAuth()
  const navigate = useNavigate()
  const [open, setOpen] = useState(false)
  const ref = useRef(null)

  useEffect(() => {
    const handleClick = (e) => {
      if (ref.current && !ref.current.contains(e.target)) {
        setOpen(false)
      }
    }
    document.addEventListener('mousedown', handleClick)
    return () => document.removeEventListener('mousedown', handleClick)
  }, [])

  const getInitials = (name) => {
    if (!name) return '?'
    return name.split(' ').map(n => n[0]).join('').toUpperCase().slice(0, 2)
  }

  const handleLogout = () => {
    auth.logout()
    navigate('/login')
  }

  const role = auth.profile?.role || 'User'
  const profileLink = role === 'Super Admin' ? '/super-admin/settings' : 
    role === 'Teacher' ? '/teacher/profile' :
    role === 'Student' ? '/student/profile' :
    role === 'Parent' ? '/parent/profile' : '/settings'
  const settingsLink = role === 'Super Admin' ? '/super-admin/settings' : '/settings'

  return (
    <div className="profile-menu" ref={ref}>
      <button className="profile-menu-btn" onClick={() => setOpen(!open)}>
        <div className="profile-menu-avatar">{getInitials(auth.profile?.full_name)}</div>
        <div className="profile-menu-info">
          <div className="profile-menu-name">{auth.profile?.full_name || auth.profile?.email}</div>
          <div className="profile-menu-role">{role}</div>
        </div>
        <span className="profile-menu-arrow">{open ? '▲' : '▼'}</span>
      </button>
      {open && (
        <div className="profile-dropdown">
          <div className="profile-dropdown-header">
            <div className="profile-dropdown-avatar">{getInitials(auth.profile?.full_name)}</div>
            <div>
              <div className="profile-dropdown-name">{auth.profile?.full_name || auth.profile?.email}</div>
              <div className="profile-dropdown-email">{auth.profile?.email}</div>
            </div>
          </div>
          <div className="profile-dropdown-divider" />
          <a href={profileLink} className="profile-dropdown-item" onClick={() => setOpen(false)}>
            <span className="profile-dropdown-icon">👤</span>
            <span>My Profile</span>
          </a>
          <a href={settingsLink} className="profile-dropdown-item" onClick={() => setOpen(false)}>
            <span className="profile-dropdown-icon">⚙️</span>
            <span>Settings</span>
          </a>
          <div className="profile-dropdown-divider" />
          <button className="profile-dropdown-item profile-dropdown-logout" onClick={handleLogout}>
            <span className="profile-dropdown-icon">🚪</span>
            <span>Logout</span>
          </button>
        </div>
      )}
    </div>
  )
}