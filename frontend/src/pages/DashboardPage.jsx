import React, { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import PageWrapper from '../components/PageWrapper'
import { useAuth } from '../hooks/useAuth.jsx'
import { listResources } from '../api'
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, LineChart, Line, PieChart, Pie, Cell } from 'recharts'

const COLORS = ['#4f46e5', '#10b981', '#f59e0b', '#ef4444']

export default function DashboardPage() {
  const auth = useAuth()
  const [summary, setSummary] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    loadSummary()
  }, [])

  const loadSummary = async () => {
    try {
      const data = await listResources(auth.token, 'dashboard/summary')
      setSummary(data)
    } catch (err) {
      console.error(err)
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return (
      <PageWrapper title="Dashboard">
        <div className="skeleton-grid">
          {Array.from({ length: 6 }).map((_, i) => <div key={i} className="skeleton-card" />)}
        </div>
      </PageWrapper>
    )
  }

  const metrics = [
    { label: 'Total Students', value: summary?.total_students || 0, color: '#4f46e5' },
    { label: 'Total Teachers', value: summary?.total_teachers || 0, color: '#10b981' },
    { label: 'Attendance %', value: `${summary?.attendance_percentage || 0}%`, color: '#f59e0b' },
    { label: 'Fee Collection', value: `$${summary?.fee_collection?.toLocaleString() || 0}`, color: '#ef4444' },
    { label: 'Pending Fees', value: summary?.pending_fees || 0, color: '#ec4899' },
    { label: 'Upcoming Exams', value: summary?.upcoming_exams || 0, color: '#8b5cf6' },
    { label: 'Upcoming Events', value: summary?.upcoming_events || 0, color: '#14b8a6' },
  ]

  const attendanceData = (summary?.monthly_attendance || []).map((d) => ({ name: ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'][d.month - 1], present: d.count }))
  const feeData = (summary?.monthly_fee_collection || []).map((d) => ({ name: ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'][d.month - 1], amount: d.total }))
  const growthData = (summary?.student_growth || []).map((d) => ({ name: ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'][d.month - 1], students: d.count }))
  const examData = (summary?.exam_performance || []).map((d) => ({ name: d.exam_name, avg: d.average_marks }))

  return (
    <PageWrapper title="Dashboard">
      <div className="welcome-banner">
        <p>Welcome, <strong>{auth.profile?.full_name || auth.profile?.email}</strong>. Role: <span className="role-badge">{auth.profile?.role}</span></p>
      </div>

      <div className="metrics-grid">
        {metrics.map((m, i) => (
          <div key={i} className="metric-card" style={{ borderTop: `3px solid ${m.color}` }}>
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
              <BarChart data={attendanceData}><CartesianGrid strokeDasharray="3 3" /><XAxis dataKey="name" /><YAxis /><Tooltip /><Bar dataKey="present" fill="#4f46e5" /></BarChart>
            </ResponsiveContainer>
          </div>
        )}
        {feeData.length > 0 && (
          <div className="chart-card">
            <h3>Monthly Fee Collection</h3>
            <ResponsiveContainer width="100%" height={250}>
              <BarChart data={feeData}><CartesianGrid strokeDasharray="3 3" /><XAxis dataKey="name" /><YAxis /><Tooltip /><Bar dataKey="amount" fill="#10b981" /></BarChart>
            </ResponsiveContainer>
          </div>
        )}
        {growthData.length > 0 && (
          <div className="chart-card">
            <h3>Student Growth</h3>
            <ResponsiveContainer width="100%" height={250}>
              <LineChart data={growthData}><CartesianGrid strokeDasharray="3 3" /><XAxis dataKey="name" /><YAxis /><Tooltip /><Line type="monotone" dataKey="students" stroke="#f59e0b" strokeWidth={2} /></LineChart>
            </ResponsiveContainer>
          </div>
        )}
        {examData.length > 0 && (
          <div className="chart-card">
            <h3>Exam Performance</h3>
            <ResponsiveContainer width="100%" height={250}>
              <BarChart data={examData}><CartesianGrid strokeDasharray="3 3" /><XAxis dataKey="name" /><YAxis /><Tooltip /><Bar dataKey="avg" fill="#8b5cf6" /></BarChart>
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
                <strong>{n.title}</strong>
                <span className="notice-date">{new Date(n.created_on).toLocaleDateString()}</span>
                <span className="notice-target">{n.target_roles || 'All'}</span>
              </div>
            ))}
          </div>
        ) : <div className="empty-state">No recent notices</div>}
      </div>

      <div className="quick-links">
        <Link to="/users" className="quick-link">User Management</Link>
        <Link to="/students" className="quick-link">Students</Link>
        <Link to="/teachers" className="quick-link">Teachers</Link>
        <Link to="/attendance" className="quick-link">Attendance</Link>
        <Link to="/exams" className="quick-link">Exams</Link>
        <Link to="/fees" className="quick-link">Fees</Link>
        <Link to="/notices" className="quick-link">Notices</Link>
        <Link to="/certificates" className="quick-link">Certificates</Link>
        <Link to="/reports" className="quick-link">Reports</Link>
        <Link to="/settings" className="quick-link">Settings</Link>
      </div>
    </PageWrapper>
  )
}
