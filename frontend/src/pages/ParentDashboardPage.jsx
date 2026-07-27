import React, { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import ParentLayout from '../components/ParentLayout'
import { useAuth } from '../hooks/useAuth.jsx'
import { listResources } from '../api'

export default function ParentDashboardPage() {
  const auth = useAuth()
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => { loadDashboard() }, [])

  const loadDashboard = async () => {
    try {
      const d = await listResources(auth.token, 'portal/parent/dashboard')
      setData(d)
    } catch (err) { console.error(err) }
    finally { setLoading(false) }
  }

  if (loading) {
    return <ParentLayout title="Dashboard"><div className="skeleton-grid">{Array.from({ length: 4 }).map((_, i) => <div key={i} className="skeleton-card" />)}</div></ParentLayout>
  }

  return (
    <ParentLayout title="Parent Dashboard">
      <div className="welcome-banner">
        <p>Welcome, <strong>{auth.profile?.full_name || auth.profile?.email}</strong></p>
        <p style={{ fontSize: '0.85rem', opacity: 0.9 }}>You have <strong>{data?.total_children || 0}</strong> registered children</p>
      </div>

      <div className="metrics-grid">
        <div className="metric-card" style={{ borderTop: '3px solid #4f46e5' }}>
          <span className="metric-label">Children</span>
          <span className="metric-value">{data?.total_children || 0}</span>
        </div>
        <div className="metric-card" style={{ borderTop: '3px solid #10b981' }}>
          <span className="metric-label">Pending Fees</span>
          <span className="metric-value">${data?.total_pending_fees || 0}</span>
        </div>
        <div className="metric-card" style={{ borderTop: '3px solid #f59e0b' }}>
          <span className="metric-label">Upcoming Exams</span>
          <span className="metric-value">{data?.upcoming_exams || 0}</span>
        </div>
        <div className="metric-card" style={{ borderTop: '3px solid #ef4444' }}>
          <span className="metric-label">Pending Homework</span>
          <span className="metric-value">{data?.pending_homework || 0}</span>
        </div>
      </div>

      <div className="card">
        <h3>👶 My Children</h3>
        {(data?.children || []).length > 0 ? (
          <div className="table-responsive">
            <table className="data-table">
              <thead>
                <tr><th>Name</th><th>Admission No</th><th>Class</th><th>Attendance</th><th>Pending Fees</th><th>Actions</th></tr>
              </thead>
              <tbody>
                {data.children.map((c) => (
                  <tr key={c.student_id}>
                    <td><strong>{c.full_name}</strong></td>
                    <td>{c.admission_no}</td>
                    <td>{c.class_name}</td>
                    <td><span className="role-badge" style={{ background: '#d1fae5', color: '#065f46' }}>{c.attendance_pct}%</span></td>
                    <td>{c.pending_fees}</td>
                    <td className="action-cell">
                      <Link to={`/parent/children/${c.student_id}/attendance`} className="btn btn-sm">Attendance</Link>
                      <Link to={`/parent/children/${c.student_id}/homework`} className="btn btn-sm">Homework</Link>
                      <Link to={`/parent/children/${c.student_id}/exams`} className="btn btn-sm">Results</Link>
                      <Link to={`/parent/children/${c.student_id}/fees`} className="btn btn-sm">Fees</Link>
                      <Link to={`/parent/children/${c.student_id}/progress`} className="btn btn-sm">Progress</Link>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : <div className="empty-state">No children registered</div>}
      </div>

      <div className="dashboard-notices" style={{ marginTop: 20 }}>
        <h3>Recent Notices</h3>
        {data?.notices?.length > 0 ? (
          <div className="notice-mini-list">
            {data.notices.map((n) => (
              <div key={n.id} className="notice-mini-item">
                <strong>{n.title}</strong>
                <span className="notice-date">{new Date(n.created_on).toLocaleDateString()}</span>
              </div>
            ))}
          </div>
        ) : <div className="empty-state">No notices</div>}
      </div>
    </ParentLayout>
  )
}
