import React from 'react'
import { NavLink, useNavigate, useLocation } from 'react-router-dom'
import { useAuth } from '../hooks/useAuth.jsx'
import NotificationBell from './NotificationBell'
import { useNotifications } from './NotificationProvider'
import ProfileMenu from './ProfileMenu'
import ThemeToggle from './ThemeToggle'
import GlobalSearch from './GlobalSearch'

const NAV_SECTIONS = [
  {
    label: 'Main',
    items: [
      { to: '/dashboard', label: 'Dashboard', icon: '??', roles: ['Super Admin', 'School Admin', 'Admin', 'Principal'] },
    ],
  },
  {
    label: 'Academics',
    items: [
      { to: '/academic-years', label: 'Academic Years', icon: '??', roles: ['Super Admin', 'School Admin', 'Admin'] },
      { to: '/classes', label: 'Classes', icon: '??', roles: ['Super Admin', 'School Admin', 'Admin'] },
      { to: '/sections', label: 'Sections', icon: '??', roles: ['Super Admin', 'School Admin', 'Admin'] },
      { to: '/subjects', label: 'Subjects', icon: '??', roles: ['Super Admin', 'School Admin', 'Admin'] },
      { to: '/subject-allocations', label: 'Allocations', icon: '??', roles: ['Super Admin', 'School Admin', 'Admin'] },
      { to: '/enrollments', label: 'Enrollments', icon: '??', roles: ['Super Admin', 'School Admin', 'Admin'] },
    ],
  },
  {
    label: 'People',
    items: [
      { to: '/users', label: 'Users', icon: '??', roles: ['Super Admin', 'School Admin', 'Admin'] },
      { to: '/students', label: 'Students', icon: '?????' },
      { to: '/teachers', label: 'Teachers', icon: '?????' },
      { to: '/parents', label: 'Parents', icon: '??' },
    ],
  },
  {
    label: 'Operations',
    items: [
      { to: '/attendance', label: 'Attendance', icon: '??' },
      { to: '/homework', label: 'Homework', icon: '??' },
      { to: '/exams', label: 'Exams', icon: '??' },
      { to: '/exam-results', label: 'Exam Results', icon: '??' },
      { to: '/timetable', label: 'Timetable', icon: '??' },
    ],
  },
  {
    label: 'Finance',
    items: [
      { to: '/fees', label: 'Fees', icon: '??' },
      { to: '/payments', label: 'Payments', icon: '??' },
    ],
  },
  {
    label: 'Communication',
    items: [
      { to: '/notices', label: 'Notices', icon: '??' },
      { to: '/events', label: 'Events', icon: '??' },
    ],
  },
  {
    label: 'Reports',
    items: [
      { to: '/report-cards', label: 'Report Cards', icon: '??' },
      { to: '/certificates', label: 'Certificates', icon: '??' },
      { to: '/reports', label: 'Reports', icon: '??' },
    ],
  },
  {
    label: 'System',
    items: [
      { to: '/settings', label: 'Organization Settings', icon: '??' },
      { to: '/notifications', label: 'Notifications', icon: '??' },
    ],
  },
]

export default function SchoolAdminLayout({ title, children, breadcrumbs }) {
  const auth = useAuth()
  const navigate = useNavigate()
  const location = useLocation()
  const { unreadCount } = useNotifications()

  const getInitials = (name) => {
    if (!name) return 'A'
    return name.split(' ').map(n => n[0]).join('').toUpperCase().slice(0, 2)
  }

  const canShow = (roles) => {
    if (!roles) return true
    return auth.hasRole(roles)
  }

  return (
    <div className="app-layout">
      <aside className="sidebar">
        <div className="sidebar-logo">
          <div className="logo-icon">?</div>
          <span className="logo-text">School ERP</span>
        </div>
        {NAV_SECTIONS.map((section) => {
          const visibleItems = section.items.filter(item => canShow(item.roles))
          if (visibleItems.length === 0) return null
          return (
            <div key={section.label}>
              <div className="sidebar-section-label">{section.label}</div>
              <nav className="sidebar-nav">
                {visibleItems.map((item) => {
                  const isActive = location.pathname === item.to || location.pathname.startsWith(item.to + '/')
                  return (
                    <NavLink
                      key={item.to}
                      to={item.to}
                      className={`sidebar-link ${isActive ? 'active' : ''}`}
                      end={item.to === '/dashboard'}
                    >
                      <span className="icon">{item.icon}</span>
                      <span className="sidebar-label">{item.label}</span>
                    </NavLink>
                  )
                })}
              </nav>
            </div>
          )
        })}
        <div className="sidebar-footer">
          <div className="sidebar-user">
            <div className="sidebar-user-avatar">
              {getInitials(auth.profile?.full_name)}
            </div>
            <div className="sidebar-user-info">
              <div className="sidebar-user-name">{auth.profile?.full_name || auth.profile?.email}</div>
              <div className="sidebar-user-role">{auth.profile?.role || 'Admin'}</div>
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
            <GlobalSearch />
            <ThemeToggle />
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
