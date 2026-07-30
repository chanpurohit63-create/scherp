import React, { useEffect, useState } from 'react'
import ParentLayout from '../components/ParentLayout'
import { useAuth } from '../hooks/useAuth.jsx'
import { listResources } from '../api'

export default function ParentEventsPage() {
  const auth = useAuth()
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => { loadEvents() }, [])

  const loadEvents = async () => {
    try {
      const d = await listResources(auth.token, 'portal/parent/calendar')
      setData(d)
    } catch (err) { console.error(err) }
    finally { setLoading(false) }
  }

  if (loading) {
    return <ParentLayout title="Events"><div className="skeleton-list"><div className="skeleton-row" /></div></ParentLayout>
  }

  return (
    <ParentLayout title="Events">
      <div className="card">
        <h3>📅 Upcoming Events</h3>
        {(data?.events || []).length > 0 ? (
          <div className="notice-list">
            {data.events.map((e) => (
              <div key={e.id} className="notice-card">
                <div className="notice-header">
                  <h3>{e.title}</h3>
                  <span className="notice-date">{new Date(e.start_date).toLocaleDateString()}</span>
                </div>
                <div className="notice-content">{e.description || ''}</div>
                <div className="notice-meta">
                  <span className="notice-tag">{e.event_type || 'Event'}</span>
                  {e.end_date && <span>Ends: {new Date(e.end_date).toLocaleDateString()}</span>}
                </div>
              </div>
            ))}
          </div>
        ) : <div className="empty-state">No upcoming events</div>}
      </div>

      <div className="card" style={{ marginTop: 20 }}>
        <h3>📝 Upcoming Exams</h3>
        {(data?.exams || []).length > 0 ? (
          <div className="table-responsive">
            <table className="data-table">
              <thead>
                <tr><th>Exam Name</th><th>Start Date</th><th>End Date</th></tr>
              </thead>
              <tbody>
                {data.exams.map((e) => (
                  <tr key={e.id}>
                    <td><strong>{e.name}</strong></td>
                    <td>{e.start_date ? new Date(e.start_date).toLocaleDateString() : '-'}</td>
                    <td>{e.end_date ? new Date(e.end_date).toLocaleDateString() : '-'}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : <div className="empty-state">No upcoming exams</div>}
      </div>
    </ParentLayout>
  )
}