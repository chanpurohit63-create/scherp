import React, { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import SchoolAdminLayout from '../components/SchoolAdminLayout'
import { useAuth } from '../hooks/useAuth.jsx'
import { listResources } from '../api'
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, LineChart, Line, PieChart, Pie, Cell } from 'recharts'

const COLORS = ['#4f46e5', '#10b981', '#f59e0b', '#ef4444']

export default function DashboardPage() {
  const auth = useAuth()
  const [summary, setSummary] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    loadSummary()
  }, [])

  const loadSummary = async () => {
    try {
      const data = await listResources(auth.token, 'dashboard/summary')
      setSummary(data)
    } catch (err) {
      console.error(err)
      setError('Failed to load dashboard data')
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return (
      <SchoolAdminLayout title="Dashboard">
        <div className="skeleton-grid">
          {Array.from({ length: 6 }).map((_, i) => <div key={i} className="skeleton-card" />)}
        </div>
      </SchoolAdminLayout>
    )
  }

  if (error) {
    return (
      <SchoolAdminLayout title="Dashboard">
        <div className="error-banner">{error}</div>
      </SchoolAdminLayout>
    )
  }

  const metrics = [
    { label: 'Total Students', value: summary?.total_students || 0, color: '#4f46e5', icon: '👨‍🎓' },
    { label: 'Total Teachers', value: summary?.total_teachers || 0, color: '#10b981', icon: '👩‍🏫' },
    { label: 'Attendance %', value: `${summary?.attendance_percentage || 0}%`, color: '#f59e0b', icon: '📋' },
    { label: 'Fee Collection', value: `$${summary?.fee_collection?.toLocaleString() || 0}`, color: '#ef4444', icon: '💰' },
    { label: 'Pending Fees', value: summary?.pending_fees || 0, color: '#ec4899', icon: '⏳' },
    { label: 'Upcoming Exams', value: summary?.upcoming_exams || 0, color: '#8b5cf6', icon: '📝' },
    { label: 'Upcoming Events', value: summary?.upcoming_events || 0, color: '#14b8a6', icon: '🎉' },
  ]

  const attendanceData = (summary?.monthly_attendance || []).map((d) => ({ name: ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'][d.month - 1], present: d.count }))
  const feeData = (summary?.monthly_fee_collection || []).map((d) => ({ name: ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'][d.month - 1], amount: d.total }))
  const growthData = (summary?.student_growth || []).map((d) => ({ name: ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'][d.month - 1], students: d.count }))
  const examData = (summary?.exam_performance || []).map((d) => ({ name: d.exam_name, avg: d.average_marks }))

  return (
    <SchoolAdminLayout title="Dashboard">
      <div className="welcome-banner">
        <div className="welcome-banner-content">
          <h2>Welcome, {auth.profile?.full_name || auth.profile?.email}</h2>
          <p>Role: <span className="badge badge-primary">{auth.profile?.role}</span></p>
        </div>
        <div className="welcome-banner-actions">
          <Link to="/students" className="btn">Students</Link>
          <Link to="/teachers" className="btn">Teachers</Link>
          <Link to="/attendance" className="btn btn-primary">Attendance</Link>
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

      <div className="charts-grid">
        {attendanceData.length > 0 && (
          <div className="chart-card">
            <h3>Monthly Attendance</h3>
            <ResponsiveContainer width="100%" height={250}>
              <BarChart data={attendanceData}><CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" /><XAxis dataKey="name" /><YAxis /><Tooltip /><Bar dataKey="present" fill="#4f46e5" radius={[4,4,0,0]} /></BarChart>
            </ResponsiveContainer>
          </div>
        )}
        {feeData.length > 0 && (
          <div className="chart-card">
            <h3>Monthly Fee Collection</h3>
            <ResponsiveContainer width="100%" height={250}>
              <BarChart data={feeData}><CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" /><XAxis dataKey="name" /><YAxis /><Tooltip /><Bar dataKey="amount" fill="#10b981" radius={[4,4,0,0]} /></BarChart>
            </ResponsiveContainer>
          </div>
        )}
        {growthData.length > 0 && (
          <div className="chart-card">
            <h3>Student Growth</h3>
            <ResponsiveContainer width="100%" height={250}>
              <LineChart data={growthData}><CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" /><XAxis dataKey="name" /><YAxis /><Tooltip /><Line type="monotone" dataKey="students" stroke="#f59e0b" strokeWidth={2} dot={{ fill: '#f59e0b', r: 4 }} /></LineChart>
            </ResponsiveContainer>
          </div>
        )}
        {examData.length > 0 && (
          <div className="chart-card">
            <h3>Exam Performance</h3>
            <ResponsiveContainer width="100%" height={250}>
              <BarChart data={examData}><CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" /><XAxis dataKey="name" /><YAxis /><Tooltip /><Bar dataKey="avg" fill="#8b5cf6" radius={[4,4,0,0]} /></BarChart>
            </ResponsiveContainer>
          </div>
        )}
      </div>

      <div className="dashboard-notices">
        <h3>Recent Notices</h3>
        {summary?.notices?.length > 0 ? (
          <div className="notice-mini-list">
            {summary.notices.slice(0, 5).map((n) => (
              <div key={n.id} className="notice-mini-item">
                <div className="notice-mini-content">
                  <div className="notice-mini-title">{n.title}</div>
                  <div className="notice-mini-text">{n.target_roles || 'All'}</div>
                </div>
                <span className="notice-date">{new Date(n.created_on).toLocaleDateString()}</span>
              </div>
            ))}
          </div>
        ) : <div className="empty-state">No recent notices</div>}
      </div>

      <div className="quick-links">
        <Link to="/users" className="quick-link"><span className="quick-link-icon">👥</span>User Mgmt</Link>
        <Link to="/students" className="quick-link"><span className="quick-link-icon">👨‍🎓</span>Students</Link>
        <Link to="/teachers" className="quick-link"><span className="quick-link-icon">👩‍🏫</span>Teachers</Link>
        <Link to="/attendance" className="quick-link"><span className="quick-link-icon">📋</span>Attendance</Link>
        <Link to="/exams" className="quick-link"><span className="quick-link-icon">📝</span>Exams</Link>
        <Link to="/fees" className="quick-link"><span className="quick-link-icon">💰</span>Fees</Link>
        <Link to="/notices" className="quick-link"><span className="quick-link-icon">📢</span>Notices</Link>
        <Link to="/certificates" className="quick-link"><span className="quick-link-icon">🎓</span>Certificates</Link>
        <Link to="/reports" className="quick-link"><span className="quick-link-icon">📈</span>Reports</Link>
        <Link to="/settings" className="quick-link"><span className="quick-link-icon">⚙️</span>Settings</Link>
      </div>
    </SchoolAdminLayout>
  )
}