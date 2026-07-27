import React, { useEffect, useState } from 'react'
import ParentLayout from '../components/ParentLayout'
import { useAuth } from '../hooks/useAuth.jsx'
import { listResources } from '../api'

export default function ParentCalendarPage() {
  const auth = useAuth()
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => { loadCalendar() }, [])

  const loadCalendar = async () => {
    try {
      const d = await listResources(auth.token, 'portal/parent/calendar')
      setData(d)
    } catch (err) { console.error(err) }
    finally { setLoading(false) }
  }

  if (loading) {
    return <ParentLayout title="Calendar"><div className="skeleton-list"><div className="skeleton-row" /></div></ParentLayout>
  }

  return (
    <ParentLayout title="Calendar">
      <div className="card">
        <h3>📅 Events</h3>
        {(data?.events || []).length > 0 ? (
          <div className="notice-list">
            {data.events.map((e) => (
              <div key={e.id} className="notice-card">
                <div className="notice-header">
                  <h3>{e.title}</h3>
                  <span className="notice-date">{new Date(e.start_date).toLocaleDateString()}</span>
                </div>
                <div className="notice-content">{e.description || ''}</div>
                <div className="notice-meta"><span className="notice-tag">{e.event_type || 'Event'}</span></div>
              </div>
            ))}
          </div>
        ) : <div className="empty-state">No events</div>}
      </div>
      <div className="card" style={{ marginTop: 20 }}>
        <h3>📝 Exams</h3>
        {(data?.exams || []).length > 0 ? (
          <div className="table-responsive">
            <table className="data-table">
              <thead><tr><th>Exam</th><th>Start</th><th>End</th></tr></thead>
              <tbody>
                {data.exams.map((e) => (
                  <tr key={e.id}><td>{e.name}</td><td>{e.start_date}</td><td>{e.end_date || '-'}</td></tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : <div className="empty-state">No exams</div>}
      </div>
    </ParentLayout>
  )
}
