import React, { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import StudentLayout from '../components/StudentLayout'
import { useAuth } from '../hooks/useAuth.jsx'
import { listResources } from '../api'
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts'

const COLORS = ['#4f46e5', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6', '#ec4899']

export default function StudentDashboardPage() {
  const auth = useAuth()
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    loadDashboard()
  }, [])

  const loadDashboard = async () => {
    try {
      const d = await listResources(auth.token, 'portal/student/dashboard')
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
      <StudentLayout title="Dashboard">
        <div className="skeleton-grid">
          {Array.from({ length: 6 }).map((_, i) => <div key={i} className="skeleton-card" />)}
        </div>
      </StudentLayout>
    )
  }

  if (error) {
    return (
      <StudentLayout title="Dashboard">
        <div className="error-banner">{error}</div>
      </StudentLayout>
    )
  }

  const student = data?.student || {}
  const attData = (data?.monthly_attendance || []).map((d) => ({
    name: ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'][d.month - 1],
    present: d.present,
    absent: d.total - d.present,
  }))
  const examData = (data?.exam_performance || []).map((d) => ({ name: d.name, pct: d.percentage }))
  const pieData = [
    { name: 'Present', value: data?.attendance_percentage || 0 },
    { name: 'Absent', value: 100 - (data?.attendance_percentage || 0) },
  ]

  return (
    <StudentLayout title="Dashboard">
      <div className="welcome-banner">
        <div className="welcome-banner-content">
          <h2>Welcome, {student.full_name || auth.profile?.email}</h2>
          <p>
            Class: {data?.class_name} | Section: {data?.section_name} | Admission: {student.admission_no}
          </p>
        </div>
        <div className="welcome-banner-actions">
          <Link to="/student/attendance" className="btn">Attendance</Link>
          <Link to="/student/homework" className="btn btn-primary">Homework</Link>
        </div>
      </div>

      <div className="metrics-grid">
        <div className="metric-card" style={{ borderTop: '3px solid #4f46e5' }}>
          <div className="metric-icon" style={{ background: '#eef2ff', color: '#4f46e5' }}>📋</div>
          <span className="metric-label">Attendance</span>
          <span className="metric-value">{data?.attendance_percentage || 0}%</span>
        </div>
        <div className="metric-card" style={{ borderTop: '3px solid #f59e0b' }}>
          <div className="metric-icon" style={{ background: '#fffbeb', color: '#f59e0b' }}>📝</div>
          <span className="metric-label">Pending Homework</span>
          <span className="metric-value">{data?.pending_homework || 0}</span>
        </div>
        <div className="metric-card" style={{ borderTop: '3px solid #10b981' }}>
          <div className="metric-icon" style={{ background: '#f0fdf4', color: '#10b981' }}>📝</div>
          <span className="metric-label">Upcoming Exams</span>
          <span className="metric-value">{data?.upcoming_exams || 0}</span>
        </div>
        <div className="metric-card" style={{ borderTop: '3px solid #ef4444' }}>
          <div className="metric-icon" style={{ background: '#fef2f2', color: '#ef4444' }}>💰</div>
          <span className="metric-label">Fee Balance</span>
          <span className="metric-value">{data?.fee_balance || 0}</span>
        </div>
        <div className="metric-card" style={{ borderTop: '3px solid #8b5cf6' }}>
          <div className="metric-icon" style={{ background: '#f5f3ff', color: '#8b5cf6' }}>💬</div>
          <span className="metric-label">Unread Messages</span>
          <span className="metric-value">{data?.unread_messages || 0}</span>
        </div>
      </div>

      <div className="charts-grid">
        {attData.length > 0 && (
          <div className="chart-card">
            <h3>Monthly Attendance</h3>
            <ResponsiveContainer width="100%" height={250}>
              <BarChart data={attData}>
                <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
                <XAxis dataKey="name" />
                <YAxis />
                <Tooltip />
                <Bar dataKey="present" fill="#4f46e5" stackId="a" radius={[4,4,0,0]} />
                <Bar dataKey="absent" fill="#f1f5f9" stackId="a" radius={[4,4,0,0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        )}
        {examData.length > 0 && (
          <div className="chart-card">
            <h3>Exam Performance</h3>
            <ResponsiveContainer width="100%" height={250}>
              <BarChart data={examData}>
                <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
                <XAxis dataKey="name" />
                <YAxis domain={[0, 100]} />
                <Tooltip />
                <Bar dataKey="pct" fill="#8b5cf6" radius={[4,4,0,0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        )}
        <div className="chart-card">
          <h3>Attendance Summary</h3>
          <ResponsiveContainer width="100%" height={250}>
            <PieChart>
              <Pie data={pieData} cx="50%" cy="50%" outerRadius={80} dataKey="value" label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}>
                {pieData.map((_, i) => <Cell key={i} fill={COLORS[i % COLORS.length]} />)}
              </Pie>
              <Tooltip />
            </PieChart>
          </ResponsiveContainer>
        </div>
      </div>

      <div className="dashboard-notices">
        <h3>Recent Notices</h3>
        {data?.notices?.length > 0 ? (
          <div className="notice-mini-list">
            {data.notices.map((n) => (
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

      <div className="dashboard-notices">
        <h3>Upcoming Events</h3>
        {data?.events?.length > 0 ? (
          <div className="notice-mini-list">
            {data.events.map((e) => (
              <div key={e.id} className="notice-mini-item">
                <div className="notice-mini-content">
                  <div className="notice-mini-title">{e.title}</div>
                </div>
                <span className="notice-date">{new Date(e.start_date).toLocaleDateString()}</span>
              </div>
            ))}
          </div>
        ) : <div className="empty-state">No upcoming events</div>}
      </div>

      <div className="quick-links">
        <Link to="/student/attendance" className="quick-link"><span className="quick-link-icon">📋</span>Attendance</Link>
        <Link to="/student/homework" className="quick-link"><span className="quick-link-icon">📝</span>Homework</Link>
        <Link to="/student/exams" className="quick-link"><span className="quick-link-icon">📝</span>Exams</Link>
        <Link to="/student/fees" className="quick-link"><span className="quick-link-icon">💰</span>Fees</Link>
        <Link to="/student/notices" className="quick-link"><span className="quick-link-icon">📢</span>Notices</Link>
        <Link to="/student/profile" className="quick-link"><span className="quick-link-icon">👤</span>Profile</Link>
      </div>
    </StudentLayout>
  )
}