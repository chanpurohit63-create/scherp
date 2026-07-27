import React, { useEffect, useState } from 'react'
import TeacherLayout from '../components/TeacherLayout'
import { useAuth } from '../hooks/useAuth.jsx'
import { listResources } from '../api'

const DAYS = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']

export default function TeacherCalendarPage() {
  const auth = useAuth()
  const [data, setData] = useState({ events: [], exams: [], timetable: [] })
  const [loading, setLoading] = useState(true)

  useEffect(() => { loadData() }, [])

  const loadData = async () => {
    try {
      const d = await listResources(auth.token, 'portal/teacher/calendar')
      setData(d || { events: [], exams: [], timetable: [] })
    } catch (err) { console.error(err) }
    finally { setLoading(false) }
  }

  if (loading) {
    return <TeacherLayout title="Calendar"><div className="skeleton-card" style={{ height: 200 }} /></TeacherLayout>
  }

  return (
    <TeacherLayout title="Calendar">
      <div className="charts-grid">
        <div className="card">
          <h3>📅 Timetable</h3>
          {data.timetable.length === 0 && <div className="empty-state">No timetable</div>}
          <div className="table-responsive">
            <table className="data-table">
              <thead><tr><th>Day</th><th>Period</th><th>Subject</th><th>Class</th><th>Room</th></tr></thead>
              <tbody>
                {data.timetable.map((item, i) => (
                  <tr key={i}>
                    <td>{DAYS[item.entry.day_of_week] || '?'}</td>
                    <td>Period {item.entry.period}</td>
                    <td>{item.subject?.name || '-'}</td>
                    <td>{item.class?.name || '-'}</td>
                    <td>{item.entry.room || '-'}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        <div className="card">
          <h3>📝 Upcoming Exams</h3>
          {data.exams.length === 0 && <div className="empty-state">No exams</div>}
          <div className="notice-list">
            {data.exams.map((exam) => (
              <div key={exam.id} className="notice-card">
                <strong>{exam.name}</strong>
                <div className="notice-meta">
                  <span>{exam.start_date ? new Date(exam.start_date).toLocaleDateString() : '-'}</span>
                </div>
              </div>
            ))}
          </div>
        </div>

        <div className="card">
          <h3>🎉 Events</h3>
          {data.events.length === 0 && <div className="empty-state">No events</div>}
          <div className="notice-list">
            {data.events.map((event) => (
              <div key={event.id} className="notice-card">
                <strong>{event.title}</strong>
                <div className="notice-meta">
                  <span>{new Date(event.start_date).toLocaleDateString()}</span>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </TeacherLayout>
  )
}

