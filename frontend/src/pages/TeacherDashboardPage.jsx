import React, { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import TeacherLayout from '../components/TeacherLayout'
import { useAuth } from '../hooks/useAuth.jsx'
import { listResources } from '../api'
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts'

const COLORS = ['#4f46e5', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6', '#ec4899']

export default function TeacherDashboardPage() {
  const auth = useAuth()
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    loadDashboard()
  }, [])

  const loadDashboard = async () => {
    try {
      const d = await listResources(auth.token, 'portal/teacher/dashboard')
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
      <TeacherLayout title="Dashboard">
        <div className="skeleton-grid">
          {Array.from({ length: 6 }).map((_, i) => <div key={i} className="skeleton-card" />)}
        </div>
      </TeacherLayout>
    )
  }

  if (error) {
    return (
      <TeacherLayout title="Dashboard">
        <div className="error-banner">{error}</div>
      </TeacherLayout>
    )
  }

  const metrics = [
    { label: 'My Classes', value: data?.total_classes || 0, color: '#4f46e5', icon: '🏫' },
    { label: 'Total Students', value: data?.total_students || 0, color: '#10b981', icon: '👨‍🎓' },
    { label: 'Today\'s Attendance', value: data?.today_attendance || 0, color: '#f59e0b', icon: '📋' },
    { label: 'Pending Homework', value: data?.pending_homework || 0, color: '#ef4444', icon: '📝' },
    { label: 'Upcoming Exams', value: data?.upcoming_exams || 0, color: '#8b5cf6', icon: '📝' },
    { label: 'Unread Messages', value: data?.unread_messages || 0, color: '#ec4899', icon: '💬' },
  ]

  return (
    <TeacherLayout title="Dashboard">
      <div className="welcome-banner">
        <div className="welcome-banner-content">
          <h2>Welcome, {auth.profile?.full_name || auth.profile?.email}</h2>
          <p>Stay on top of your classes, assignments, and student progress</p>
        </div>
        <div className="welcome-banner-actions">
          <Link to="/teacher/classes" className="btn">My Classes</Link>
          <Link to="/teacher/attendance" className="btn btn-primary">Take Attendance</Link>
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

      <div className="quick-links">
        <Link to="/teacher/classes" className="quick-link"><span className="quick-link-icon">🏫</span>My Classes</Link>
        <Link to="/teacher/attendance" className="quick-link"><span className="quick-link-icon">📋</span>Attendance</Link>
        <Link to="/teacher/homework" className="quick-link"><span className="quick-link-icon">📝</span>Homework</Link>
        <Link to="/teacher/exams" className="quick-link"><span className="quick-link-icon">📝</span>Exams</Link>
        <Link to="/teacher/students" className="quick-link"><span className="quick-link-icon">👨‍🎓</span>Students</Link>
        <Link to="/teacher/notices" className="quick-link"><span className="quick-link-icon">📢</span>Notices</Link>
        <Link to="/teacher/calendar" className="quick-link"><span className="quick-link-icon">📅</span>Calendar</Link>
        <Link to="/teacher/profile" className="quick-link"><span className="quick-link-icon">👤</span>Profile</Link>
      </div>
    </TeacherLayout>
  )
}