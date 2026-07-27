import React, { useEffect, useState } from 'react'
import TeacherLayout from '../components/TeacherLayout'
import { useAuth } from '../hooks/useAuth.jsx'
import { listResources } from '../api'

export default function TeacherDashboardPage() {
  const auth = useAuth()
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => { loadDashboard() }, [])

  const loadDashboard = async () => {
    try {
      const d = await listResources(auth.token, 'portal/teacher/dashboard')
      setData(d)
    } catch (err) { console.error(err) }
    finally { setLoading(false) }
  }

  if (loading) {
    return <TeacherLayout title="Dashboard"><div className="skeleton-grid">{Array.from({ length: 6 }).map((_, i) => <div key={i} className="skeleton-card" />)}</div></TeacherLayout>
  }

  const metrics = [
    { label: 'Assigned Classes', value: data?.assigned_classes?.length || 0, color: '#4f46e5' },
    { label: 'Total Students', value: data?.total_students || 0, color: '#10b981' },
    { label: "Today's Attendance", value: data?.today_attendance || 0, color: '#f59e0b' },
    { label: 'Pending Homework', value: data?.pending_homework || 0, color: '#ef4444' },
    { label: 'Upcoming Exams', value: data?.upcoming_exams || 0, color: '#8b5cf6' },
    { label: 'Unread Messages', value: data?.unread_messages || 0, color: '#ec4899' },
  ]

  return (
    <TeacherLayout title="Teacher Dashboard">
      <div className="welcome-banner">
        <p>Welcome, <strong>{data?.teacher?.full_name || auth.profile?.full_name}</strong>. Employee No: <span className="role-badge">{data?.teacher?.employee_no}</span></p>
      </div>
      <div className="metrics-grid">
        {metrics.map((m, i) => (
          <div key={i} className="metric-card" style={{ borderTop: `3px solid ${m.color}` }}>
            <span className="metric-label">{m.label}</span>
            <span className="metric-value">{m.value}</span>
          </div>
        ))}
      </div>
      <div className="card">
        <h3>📚 Assigned Classes</h3>
        {(data?.assigned_classes || []).length > 0 ? (
          <div className="table-responsive">
            <table className="data-table">
              <thead><tr><th>Class</th></tr></thead>
              <tbody>
                {data.assigned_classes.map((c) => (
                  <tr key={c.id}><td><strong>{c.name}</strong></td></tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : <div className="empty-state">No classes assigned</div>}
      </div>
    </TeacherLayout>
  )
}
