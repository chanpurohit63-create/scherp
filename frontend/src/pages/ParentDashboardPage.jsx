import React, { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import ParentLayout from '../components/ParentLayout'
import { useAuth } from '../hooks/useAuth.jsx'
import { useParentChild } from '../components/ParentChildContext'
import { listResources, downloadFile } from '../api'
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, LineChart, Line, PieChart, Pie, Cell } from 'recharts'

const COLORS = ['#4f46e5', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6', '#ec4899']

export default function ParentDashboardPage() {
  const auth = useAuth()
  const { children, activeChild, activeChildId } = useParentChild()
  const [data, setData] = useState(null)
  const [progressData, setProgressData] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => { loadDashboard() }, [activeChildId])

  const loadDashboard = async () => {
    setLoading(true)
    try {
      const d = await listResources(auth.token, 'portal/parent/dashboard')
      setData(d)
      if (activeChildId) {
        try {
          const p = await listResources(auth.token, `portal/parent/children/${activeChildId}/progress`)
          setProgressData(p)
        } catch (err) { /* progress may not be available */ }
      }
    } catch (err) { console.error(err) }
    finally { setLoading(false) }
  }

  const handleReportCard = () => {
    if (activeChildId) {
      downloadFile(auth.token, `portal/parent/children/${activeChildId}/results/report-card`, 'report_card.pdf')
    }
  }

  if (loading) {
    return (
      <ParentLayout title="Dashboard">
        <div className="welcome-banner skeleton">
          <div className="skeleton-card" style={{ height: 60 }} />
        </div>
        <div className="metrics-grid">
          {Array.from({ length: 4 }).map((_, i) => <div key={i} className="skeleton-card" style={{ height: 80 }} />)}
        </div>
        <div className="skeleton-card" style={{ height: 200, marginTop: 20 }} />
      </ParentLayout>
    )
  }

  const attTrend = (progressData?.attendance_trend || [])
    .map((d) => ({
      name: ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'][d.month - 1],
      pct: d.pct
    })).filter(d => d.pct > 0)

  const academicTrend = (progressData?.academic_trend || [])

  const hwCompletion = progressData?.homework_completion || {}
  const hwData = [
    { name: 'Completed', value: hwCompletion.completed || 0 },
    { name: 'Pending', value: hwCompletion.pending || 0 },
    { name: 'Late', value: hwCompletion.late || 0 },
  ].filter(d => d.value > 0)

  const subjectPerf = (progressData?.subject_performance || [])

  return (
    <ParentLayout title="Parent Dashboard">
      {/* Welcome Banner */}
      <div className="welcome-banner">
        <div className="welcome-banner-content">
          <h2>Welcome, <strong>{auth.profile?.full_name || auth.profile?.email}</strong> 👋</h2>
          <p>You have <strong>{data?.total_children || 0}</strong> registered child{data?.total_children !== 1 ? 'ren' : ''}</p>
        </div>
        {activeChild && (
          <div className="welcome-banner-actions">
            <button className="btn btn-primary btn-sm" onClick={handleReportCard}>📄 Report Card</button>
          </div>
        )}
      </div>

      {/* Metrics Cards */}
      <div className="metrics-grid">
        <div className="metric-card" style={{ borderTop: '3px solid #4f46e5' }}>
          <span className="metric-label">👶 Children</span>
          <span className="metric-value">{data?.total_children || 0}</span>
        </div>
        <div className="metric-card" style={{ borderTop: '3px solid #10b981' }}>
          <span className="metric-label">💰 Pending Fees</span>
          <span className="metric-value">${data?.total_pending_fees || 0}</span>
        </div>
        <div className="metric-card" style={{ borderTop: '3px solid #f59e0b' }}>
          <span className="metric-label">📝 Upcoming Exams</span>
          <span className="metric-value">{data?.upcoming_exams || 0}</span>
        </div>
        <div className="metric-card" style={{ borderTop: '3px solid #ef4444' }}>
          <span className="metric-label">📚 Pending Homework</span>
          <span className="metric-value">{data?.pending_homework || 0}</span>
        </div>
      </div>

      {/* My Children Quick View */}
      <div className="card">
        <div className="card-header">
          <h3>👨‍👩‍👧‍👦 My Children</h3>
          <Link to="/parent/children" className="btn btn-sm">View All</Link>
        </div>
        {(data?.children || []).length > 0 ? (
          <div className="table-responsive">
            <table className="data-table">
              <thead>
                <tr>
                  <th>Name</th>
                  <th>Admission No</th>
                  <th>Class</th>
                  <th>Attendance</th>
                  <th>Pending Fees</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                {data.children.map((c) => (
                  <tr key={c.student_id} className={c.student_id === activeChildId ? 'active-row' : ''}>
                    <td><strong>{c.full_name}</strong></td>
                    <td>{c.admission_no}</td>
                    <td>{c.class_name}</td>
                    <td>
                      <span className="role-badge" style={{ background: '#d1fae5', color: '#065f46' }}>
                        {c.attendance_pct}%
                      </span>
                    </td>
                    <td>{c.pending_fees}</td>
                    <td className="action-cell">
                      <Link to={`/parent/children/${c.student_id}/attendance`} className="btn btn-sm">📋</Link>
                      <Link to={`/parent/children/${c.student_id}/homework`} className="btn btn-sm">📝</Link>
                      <Link to={`/parent/children/${c.student_id}/exams`} className="btn btn-sm">🏆</Link>
                      <Link to={`/parent/children/${c.student_id}/fees`} className="btn btn-sm">💰</Link>
                      <Link to={`/parent/children/${c.student_id}/progress`} className="btn btn-sm">📈</Link>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : <div className="empty-state">No children registered</div>}
      </div>

      {/* Performance Charts for Active Child */}
      {activeChild && (
        <div className="card" style={{ marginTop: 20 }}>
          <div className="card-header">
            <h3>📈 Performance - {activeChild.full_name}</h3>
          </div>
          <div className="charts-grid">
            {attTrend.length > 0 && (
              <div className="chart-card">
                <h4>Attendance Trend</h4>
                <ResponsiveContainer width="100%" height={200}>
                  <LineChart data={attTrend}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="name" />
                    <YAxis domain={[0, 100]} />
                    <Tooltip />
                    <Line type="monotone" dataKey="pct" stroke="#4f46e5" strokeWidth={2} />
                  </LineChart>
                </ResponsiveContainer>
              </div>
            )}
            {academicTrend.length > 0 && (
              <div className="chart-card">
                <h4>Academic Performance</h4>
                <ResponsiveContainer width="100%" height={200}>
                  <BarChart data={academicTrend}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="name" />
                    <YAxis domain={[0, 100]} />
                    <Tooltip />
                    <Bar dataKey="pct" fill="#8b5cf6" />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            )}
            {hwData.length > 0 && (
              <div className="chart-card">
                <h4>Homework</h4>
                <ResponsiveContainer width="100%" height={200}>
                  <PieChart>
                    <Pie data={hwData} cx="50%" cy="50%" innerRadius={50} outerRadius={80} dataKey="value" label>
                      {hwData.map((_, i) => <Cell key={i} fill={COLORS[i % COLORS.length]} />)}
                    </Pie>
                    <Tooltip />
                  </PieChart>
                </ResponsiveContainer>
              </div>
            )}
            {subjectPerf.length > 0 && (
              <div className="chart-card">
                <h4>Subject Performance</h4>
                <ResponsiveContainer width="100%" height={200}>
                  <BarChart data={subjectPerf}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="name" />
                    <YAxis domain={[0, 100]} />
                    <Tooltip />
                    <Bar dataKey="pct" fill="#10b981" />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            )}
          </div>
          {attTrend.length === 0 && academicTrend.length === 0 && hwData.length === 0 && subjectPerf.length === 0 && (
            <div className="empty-state">No performance data available yet</div>
          )}
        </div>
      )}

      {/* Recent Notices */}
      <div className="dashboard-notices" style={{ marginTop: 20 }}>
        <div className="card">
          <div className="card-header">
            <h3>📢 Recent Notices</h3>
            <Link to="/parent/notices" className="btn btn-sm">View All</Link>
          </div>
          {data?.notices?.length > 0 ? (
            <div className="notice-mini-list">
              {data.notices.map((n) => (
                <div key={n.id} className="notice-mini-item">
                  <div className="notice-mini-content">
                    <strong>{n.title}</strong>
                    <p className="notice-mini-text">{n.content?.substring(0, 100)}{n.content?.length > 100 ? '...' : ''}</p>
                  </div>
                  <span className="notice-date">{new Date(n.created_on).toLocaleDateString()}</span>
                </div>
              ))}
            </div>
          ) : <div className="empty-state">No notices</div>}
        </div>
      </div>
    </ParentLayout>
  )
}