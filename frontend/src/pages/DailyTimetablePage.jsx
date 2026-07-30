import React, { useEffect, useState } from 'react'
import PageWrapper from '../components/PageWrapper'
import { useAuth } from '../hooks/useAuth.jsx'
import { listResources, getBackendUrl } from '../api'

const DAY_NAMES = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']

export default function DailyTimetablePage() {
  const auth = useAuth()
  const [entries, setEntries] = useState([])
  const [loading, setLoading] = useState(true)
  const [dayFilter, setDayFilter] = useState(new Date().getDay() === 0 ? 6 : new Date().getDay() - 1)
  const [classId, setClassId] = useState('')
  const [teacherId, setTeacherId] = useState('')

  useEffect(() => {
    loadTimetable()
  }, [])

  const loadTimetable = async () => {
    try {
      const params = new URLSearchParams()
      params.set('day_of_week', dayFilter)
      if (classId) params.set('class_id', classId)
      if (teacherId) params.set('teacher_id', teacherId)
      const data = await listResources(auth.token, `timetable?${params.toString()}`)
      setEntries(data)
    } catch (err) {
      console.error(err)
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return (
      <PageWrapper title="Daily Timetable">
        <div className="skeleton-grid">
          {Array.from({ length: 4 }).map((_, i) => <div key={i} className="skeleton-card" />)}
        </div>
      </PageWrapper>
    )
  }

  return (
    <PageWrapper title="Daily Timetable">
      <form onSubmit={(e) => { e.preventDefault(); loadTimetable(); }} className="flex gap-4 mb-6 flex-wrap items-end">
        <div className="form-group">
          <label>Day</label>
          <select value={dayFilter} onChange={(e) => setDayFilter(parseInt(e.target.value))} className="input">
            {DAY_NAMES.map((d, i) => <option key={i} value={i}>{d}</option>)}
          </select>
        </div>
        <div className="form-group">
          <label>Class ID</label>
          <input type="number" value={classId} onChange={(e) => setClassId(e.target.value)} className="input" />
        </div>
        <div className="form-group">
          <label>Teacher ID</label>
          <input type="number" value={teacherId} onChange={(e) => setTeacherId(e.target.value)} className="input" />
        </div>
        <button type="submit" className="btn btn-primary">View</button>
      </form>

      <div className="card">
        <h3 className="card-title">{DAY_NAMES[dayFilter]} Schedule</h3>
        <div className="table-responsive">
          <table className="table">
            <thead>
              <tr>
                <th>Period</th>
                <th>Start</th>
                <th>End</th>
                <th>Class</th>
                <th>Section</th>
                <th>Subject</th>
                <th>Teacher</th>
                <th>Room</th>
                <th>Status</th>
              </tr>
            </thead>
            <tbody>
              {entries.length === 0 && (
                <tr><td colSpan={9} className="text-center">No classes scheduled for this day</td></tr>
              )}
              {entries.map((entry) => (
                <tr key={entry.id}>
                  <td><strong>P{entry.period}</strong></td>
                  <td>{entry.start_time || '-'}</td>
                  <td>{entry.end_time || '-'}</td>
                  <td>{entry.class_id}</td>
                  <td>{entry.section_id || '-'}</td>
                  <td>{entry.subject_id}</td>
                  <td>{entry.teacher_id}</td>
                  <td>{entry.room_id || '-'}</td>
                  <td><span className={`badge ${entry.status === 'active' ? 'badge-success' : 'badge-warning'}`}>{entry.status}</span></td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </PageWrapper>
  )
}