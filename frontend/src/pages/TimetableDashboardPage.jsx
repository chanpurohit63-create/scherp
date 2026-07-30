import React, { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import PageWrapper from '../components/PageWrapper'
import { useAuth } from '../hooks/useAuth.jsx'
import { listResources, getBackendUrl } from '../api'

const DAY_NAMES = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']

export default function TimetableDashboardPage() {
  const auth = useAuth()
  const [dashboard, setDashboard] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    loadDashboard()
  }, [])

  const loadDashboard = async () => {
    try {
      const data = await listResources(auth.token, 'timetable/dashboard')
      setDashboard(data)
    } catch (err) {
      console.error(err)
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return (
      <PageWrapper title="Timetable Dashboard">
        <div className="skeleton-grid">
          {Array.from({ length: 6 }).map((_, i) => <div key={i} className="skeleton-card" />)}
        </div>
      </PageWrapper>
    )
  }

  const metrics = [
    { label: 'Total Classes', value: dashboard?.total_classes || 0, color: '#4f46e5' },
    { label: 'Total Teachers', value: dashboard?.total_teachers || 0, color: '#10b981' },
    { label: "Today's Classes", value: dashboard?.today_classes || 0, color: '#f59e0b' },
    { label: 'Running Now', value: dashboard?.running_classes || 0, color: '#ef4444' },
    { label: 'Free Rooms', value: dashboard?.free_rooms || 0, color: '#14b8a6' },
    { label: 'Occupied Rooms', value: dashboard?.occupied_rooms || 0, color: '#8b5cf6' },
    { label: 'Teacher Utilization', value: `${dashboard?.teacher_utilization || 0}%`, color: '#ec4899' },
    { label: 'Room Utilization', value: `${dashboard?.room_utilization || 0}%`, color: '#06b6d4' },
    { label: 'Avg Teaching Hours', value: dashboard?.avg_teaching_hours || 0, color: '#84cc16' },
  ]

  return (
    <PageWrapper title="Timetable Dashboard">
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

      <div className="flex gap-4 mt-6 flex-wrap">
        <Link to="/timetable/weekly" className="btn btn-primary">View Weekly Timetable</Link>
        <Link to="/timetable/generator" className="btn btn-secondary">Auto-Generate Timetable</Link>
        <Link to="/timetable/conflicts" className="btn btn-warning">Conflict Monitor</Link>
        <Link to="/timetable/periods" className="btn btn-secondary">Period Master</Link>
        <Link to="/timetable/rooms" className="btn btn-secondary">Room Management</Link>
        <Link to="/timetable/teacher-availability" className="btn btn-secondary">Teacher Availability</Link>
      </div>

      {dashboard?.upcoming_classes && dashboard.upcoming_classes.length > 0 && (
        <div className="card mt-6">
          <h3 className="card-title">Upcoming Classes</h3>
          <div className="table-responsive">
            <table className="table">
              <thead>
                <tr>
                  <th>Day</th>
                  <th>Period</th>
                  <th>Start</th>
                  <th>End</th>
                  <th>Class</th>
                  <th>Subject</th>
                  <th>Teacher</th>
                  <th>Room</th>
                </tr>
              </thead>
              <tbody>
                {dashboard.upcoming_classes.map((cls, i) => (
                  <tr key={i}>
                    <td>{DAY_NAMES[cls.day_of_week] || cls.day_of_week}</td>
                    <td>{cls.period}</td>
                    <td>{cls.start_time}</td>
                    <td>{cls.end_time}</td>
                    <td>{cls.class_id}</td>
                    <td>{cls.subject_id}</td>
                    <td>{cls.teacher_id}</td>
                    <td>{cls.room_id || '-'}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </PageWrapper>
  )
}