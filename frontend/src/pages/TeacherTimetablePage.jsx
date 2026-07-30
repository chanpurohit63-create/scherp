import React, { useEffect, useState } from 'react'
import PageWrapper from '../components/PageWrapper'
import { useAuth } from '../hooks/useAuth.jsx'
import { listResources, getBackendUrl } from '../api'

const DAY_NAMES = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']

export default function TeacherTimetablePage() {
  const auth = useAuth()
  const [timetable, setTimetable] = useState([])
  const [loading, setLoading] = useState(true)
  const [teacherId, setTeacherId] = useState('')
  const [academicYearId, setAcademicYearId] = useState('')

  useEffect(() => {
    loadTimetable()
  }, [])

  const loadTimetable = async () => {
    try {
      const tid = teacherId || auth.profile?.id
      const params = new URLSearchParams()
      if (academicYearId) params.set('academic_year_id', academicYearId)
      const data = await listResources(auth.token, `teachers/${tid}/timetable?${params.toString()}`)
      setTimetable(data)
    } catch (err) {
      console.error(err)
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return (
      <PageWrapper title="My Timetable">
        <div className="skeleton-grid">
          {Array.from({ length: 4 }).map((_, i) => <div key={i} className="skeleton-card" />)}
        </div>
      </PageWrapper>
    )
  }

  const today = new Date().getDay()
  const todayIndex = today === 0 ? 6 : today - 1

  const currentPeriod = timetable.filter((e) => e.day_of_week === todayIndex && e.start_time && e.end_time)
  const now = new Date()
  const currentTime = `${now.getHours().toString().padStart(2, '0')}:${now.getMinutes().toString().padStart(2, '0')}`
  const runningNow = currentPeriod.find((p) => p.start_time <= currentTime && p.end_time >= currentTime)

  const freePeriods = timetable.filter((e) => e.day_of_week === todayIndex && !runningNow)
  const occupiedPeriods = timetable.filter((e) => e.day_of_week === todayIndex && runningNow)

  return (
    <PageWrapper title="My Timetable">
      <div className="flex gap-4 mb-6 flex-wrap">
        <div className="form-group">
          <label>Teacher ID</label>
          <input type="number" value={teacherId} onChange={(e) => setTeacherId(e.target.value)} className="input" placeholder="Filter by teacher ID" />
        </div>
        <div className="form-group">
          <label>Academic Year</label>
          <input type="number" value={academicYearId} onChange={(e) => setAcademicYearId(e.target.value)} className="input" placeholder="Filter by year" />
        </div>
        <button onClick={loadTimetable} className="btn btn-primary">Apply</button>
      </div>

      {runningNow && (
        <div className="alert alert-info mb-6">
          <strong>Current Period:</strong> {runningNow.start_time} - {runningNow.end_time} | Subject: {runningNow.subject_id} | Class: {runningNow.class_id} | Room: {runningNow.room_id || '-'}
        </div>
      )}

      <div className="metrics-grid mb-6">
        <div className="metric-card">
          <span className="metric-label">Total Teaching Hours Today</span>
          <span className="metric-value">{timetable.filter((e) => e.day_of_week === todayIndex).length}</span>
        </div>
        <div className="metric-card">
          <span className="metric-label">Current Period</span>
          <span className="metric-value">{runningNow ? `Period ${runningNow.period}` : 'Free'}</span>
        </div>
        <div className="metric-card">
          <span className="metric-label">Free Periods Today</span>
          <span className="metric-value">{freePeriods.length}</span>
        </div>
      </div>

      <h3 className="card-title">Weekly Schedule</h3>
      <div className="table-responsive">
        <table className="table">
          <thead>
            <tr>
              <th>Day</th>
              <th>Period</th>
              <th>Start</th>
              <th>End</th>
              <th>Subject</th>
              <th>Class</th>
              <th>Section</th>
              <th>Room</th>
              <th>Status</th>
            </tr>
          </thead>
          <tbody>
            {timetable.length === 0 && (
              <tr><td colSpan={9} className="text-center">No timetable entries found</td></tr>
            )}
            {timetable.map((entry) => (
              <tr key={entry.id} className={entry.day_of_week === todayIndex ? 'bg-highlight' : ''}>
                <td>{DAY_NAMES[entry.day_of_week]}</td>
                <td>{entry.period}</td>
                <td>{entry.start_time || '-'}</td>
                <td>{entry.end_time || '-'}</td>
                <td>{entry.subject_id}</td>
                <td>{entry.class_id}</td>
                <td>{entry.section_id || '-'}</td>
                <td>{entry.room_id || '-'}</td>
                <td><span className={`badge ${entry.status === 'active' ? 'badge-success' : 'badge-warning'}`}>{entry.status}</span></td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </PageWrapper>
  )
}