import React, { useEffect, useState } from 'react'
import PageWrapper from '../components/PageWrapper'
import { useAuth } from '../hooks/useAuth.jsx'
import { listResources, getBackendUrl } from '../api'

const DAY_NAMES = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
const PERIOD_COLORS = ['#4f46e5', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6', '#ec4899', '#14b8a6', '#06b6d4']

export default function WeeklyTimetablePage() {
  const auth = useAuth()
  const [entries, setEntries] = useState([])
  const [loading, setLoading] = useState(true)
  const [academicYearId, setAcademicYearId] = useState('')
  const [classId, setClassId] = useState('')
  const [teacherId, setTeacherId] = useState('')
  const [dayFilter, setDayFilter] = useState('')

  useEffect(() => {
    loadTimetable()
  }, [])

  const loadTimetable = async () => {
    try {
      const params = new URLSearchParams()
      if (academicYearId) params.set('academic_year_id', academicYearId)
      if (classId) params.set('class_id', classId)
      if (teacherId) params.set('teacher_id', teacherId)
      if (dayFilter !== '') params.set('day_of_week', dayFilter)
      const query = params.toString()
      const data = await listResources(auth.token, `timetable?${query}`)
      setEntries(data)
    } catch (err) {
      console.error(err)
    } finally {
      setLoading(false)
    }
  }

  const handleFilter = (e) => {
    e.preventDefault()
    loadTimetable()
  }

  const daysToShow = dayFilter !== '' ? [parseInt(dayFilter)] : [0, 1, 2, 3, 4, 5]

  if (loading) {
    return (
      <PageWrapper title="Weekly Timetable">
        <div className="skeleton-grid">
          {Array.from({ length: 4 }).map((_, i) => <div key={i} className="skeleton-card" />)}
        </div>
      </PageWrapper>
    )
  }

  return (
    <PageWrapper title="Weekly Timetable">
      <form onSubmit={handleFilter} className="flex gap-4 mb-6 flex-wrap items-end">
        <div className="form-group">
          <label>Academic Year ID</label>
          <input type="number" value={academicYearId} onChange={(e) => setAcademicYearId(e.target.value)} className="input" />
        </div>
        <div className="form-group">
          <label>Class ID</label>
          <input type="number" value={classId} onChange={(e) => setClassId(e.target.value)} className="input" />
        </div>
        <div className="form-group">
          <label>Teacher ID</label>
          <input type="number" value={teacherId} onChange={(e) => setTeacherId(e.target.value)} className="input" />
        </div>
        <div className="form-group">
          <label>Day</label>
          <select value={dayFilter} onChange={(e) => setDayFilter(e.target.value)} className="input">
            <option value="">All Days</option>
            {DAY_NAMES.map((d, i) => <option key={i} value={i}>{d}</option>)}
          </select>
        </div>
        <button type="submit" className="btn btn-primary">Filter</button>
        <button type="button" onClick={() => { setAcademicYearId(''); setClassId(''); setTeacherId(''); setDayFilter(''); loadTimetable(); }} className="btn btn-secondary">Clear</button>
      </form>

      <div className="table-responsive">
        <table className="table">
          <thead>
            <tr>
              <th>Day</th>
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
              <tr><td colSpan={10} className="text-center">No timetable entries found</td></tr>
            )}
            {entries.map((entry) => (
              <tr key={entry.id} style={{ backgroundColor: entry.status === 'cancelled' ? '#fef2f2' : 'transparent' }}>
                <td>{DAY_NAMES[entry.day_of_week] || entry.day_of_week}</td>
                <td>{entry.period}</td>
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

      <div className="mt-6">
        <h3 className="card-title">Weekly Grid View</h3>
        <div className="grid-weekly">
          {daysToShow.map((day) => (
            <div key={day} className="weekly-day-card">
              <h4 className="weekly-day-header">{DAY_NAMES[day]}</h4>
              <div className="weekly-periods">
                {entries.filter((e) => e.day_of_week === day).sort((a, b) => a.period - b.period).map((entry) => (
                  <div key={entry.id} className="weekly-period-block" style={{ borderLeftColor: PERIOD_COLORS[entry.period % PERIOD_COLORS.length] }}>
                    <div className="period-label">P{entry.period}</div>
                    <div className="period-time">{entry.start_time}-{entry.end_time}</div>
                    <div className="period-subject">Subject: {entry.subject_id}</div>
                    <div className="period-teacher">Teacher: {entry.teacher_id}</div>
                    <div className="period-room">Room: {entry.room_id || '-'}</div>
                  </div>
                ))}
              </div>
            </div>
          ))}
        </div>
      </div>
    </PageWrapper>
  )
}