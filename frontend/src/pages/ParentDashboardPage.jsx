import React, { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import ParentLayout from '../components/ParentLayout'
import { useAuth } from '../hooks/useAuth.jsx'
import { listResources } from '../api'
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts'

const COLORS = ['#4f46e5', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6', '#ec4899']

export default function ParentDashboardPage() {
  const auth = useAuth()
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    loadDashboard()
  }, [])

  const loadDashboard = async () => {
    try {
      const d = await listResources(auth.token, 'portal/parent/dashboard')
      setData(d)
    } catch (err) {
      console.error(err)
      setError('Failed to load dashboard data')
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return (
      <ParentLayout title="Dashboard" hideChildSwitcher>
        <div className="skeleton-grid">
          {Array.from({ length: 6 }).map((_, i) => <div key={i} className="skeleton-card" />)}
        </div>
      </ParentLayout>
    )
  }

  if (error) {
    return (
      <ParentLayout title="Dashboard" hideChildSwitcher>
        <div className="error-banner">{error}</div>
      </ParentLayout>
    )
  }

  const metrics = [
    { label: 'Children Enrolled', value: data?.children_count || 0, color: '#4f46e5', icon: '👨‍👩‍👧‍👦' },
    { label: 'Attendance', value: `${data?.attendance_percentage || 0}%`, color: '#10b981', icon: '📋' },
    { label: 'Pending Homework', value: data?.pending_homework || 0, color: '#f59e0b', icon: '📝' },
    { label: 'Upcoming Exams', value: data?.upcoming_exams || 0, color: '#8b5cf6', icon: '📝' },
    { label: 'Fee Balance', value: data?.fee_balance || 0, color: '#ef4444', icon: '💰' },
    { label: 'Unread Messages', value: data?.unread_messages || 0, color: '#ec4899', icon: '💬' },
  ]

  return (
    <ParentLayout title="Dashboard">
      <div className="welcome-banner">
        <div className="welcome-banner-content">
          <h2>Welcome, {auth.profile?.full_name || auth.profile?.email}</h2>
          <p>Stay connected with your child's academic journey</p>
        </div>
        <div className="welcome-banner-actions">
          <Link to="/parent/children" className="btn">My Children</Link>
          <Link to="/parent/attendance" className="btn btn-primary">Attendance</Link>
        </div>
      </div>

      <div className="metrics-grid">
        {metrics.map((m, i) => (
          <div key={i} className="metric-card" style={{ borderTop: `3px solid ${m.color}` }}>
            <div className="metric-icon" style={{ background: `${m.color}15`, color: m.color }}>{m.icon}</div>
            <span className="metric-label">{m.label}</span>
            <span className="metric-value">{m.value}</span>
          </div>
        ))}
      </div>

      <div className="dashboard-notices">
        <h3>Recent Notices</h3>
        {data?.notices?.length > 0 ? (
          <div className="notice-mini-list">
            {data.notices.slice(0, 5).map((n) => (
              <div key={n.id} className="notice-mini-item">
                <div className="notice-mini-content">
                  <div className="notice-mini-title">{n.title}</div>
                </div>
                <span className="notice-date">{new Date(n.created_on).toLocaleDateString()}</span>
              </div>
            ))}
          </div>
        ) : <div className="empty-state">No recent notices</div>}
      </div>

      <div className="quick-links">
        <Link to="/parent/children" className="quick-link"><span className="quick-link-icon">👨‍👩‍👧‍👦</span>My Children</Link>
        <Link to="/parent/attendance" className="quick-link"><span className="quick-link-icon">📋</span>Attendance</Link>
        <Link to="/parent/homework" className="quick-link"><span className="quick-link-icon">📝</span>Homework</Link>
        <Link to="/parent/exams" className="quick-link"><span className="quick-link-icon">🏆</span>Exam Results</Link>
        <Link to="/parent/fees" className="quick-link"><span className="quick-link-icon">💰</span>Fees</Link>
        <Link to="/parent/notices" className="quick-link"><span className="quick-link-icon">📢</span>Notices</Link>
        <Link to="/parent/events" className="quick-link"><span className="quick-link-icon">📅</span>Events</Link>
        <Link to="/parent/profile" className="quick-link"><span className="quick-link-icon">👤</span>Profile</Link>
      </div>
    </ParentLayout>
  )
}