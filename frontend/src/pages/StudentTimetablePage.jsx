import React, { useEffect, useState } from 'react'
import PageWrapper from '../components/PageWrapper'
import { useAuth } from '../hooks/useAuth.jsx'
import { listResources, getBackendUrl } from '../api'

const DAY_NAMES = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']

export default function StudentTimetablePage() {
  const auth = useAuth()
  const [timetable, setTimetable] = useState([])
  const [loading, setLoading] = useState(true)
  const [studentId, setStudentId] = useState('')
  const [academicYearId, setAcademicYearId] = useState('')

  useEffect(() => {
    loadTimetable()
  }, [])

  const loadTimetable = async () => {
    try {
      const sid = studentId || auth.profile?.id
      const params = new URLSearchParams()
      if (academicYearId) params.set('academic_year_id', academicYearId)
      const data = await listResources(auth.token, `students/${sid}/timetable?${params.toString()}`)
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
  const todayClasses = timetable.filter((e) => e.day_of_week === todayIndex)

  return (
    <PageWrapper title="My Timetable">
      <div className="flex gap-4 mb-6 flex-wrap">
        <div className="form-group">
          <label>Student ID</label>
          <input type="number" value={studentId} onChange={(e) => setStudentId(e.target.value)} className="input" placeholder="Filter by student ID" />
        </div>
        <div className="form-group">
          <label>Academic Year</label>
          <input type="number" value={academicYearId} onChange={(e) => setAcademicYearId(e.target.value)} className="input" placeholder="Filter by year" />
        </div>
        <button onClick={loadTimetable} className="btn btn-primary">Apply</button>
      </div>

      <h3 className="card-title">Today's Schedule</h3>
      {todayClasses.length === 0 ? (
        <p className="text-muted">No classes scheduled for today.</p>
      ) : (
        <div className="table-responsive">
          <table className="table">
            <thead>
              <tr><th>Period</th><th>Start</th><th>End</th><th>Subject</th><th>Teacher</th><th>Room</th><th>Class</th><th>Section</th></tr>
            </thead>
            <tbody>
              {todayClasses.map((entry) => (
                <tr key={entry.id}>
                  <td>{entry.period}</td>
                  <td>{entry.start_time || '-'}</td>
                  <td>{entry.end_time || '-'}</td>
                  <td>{entry.subject_id}</td>
                  <td>{entry.teacher_id}</td>
                  <td>{entry.room_id || '-'}</td>
                  <td>{entry.class_id}</td>
                  <td>{entry.section_id || '-'}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      <h3 className="card-title mt-6">Weekly Timetable</h3>
      <div className="table-responsive">
        <table className="table">
          <thead>
            <tr>
              <th>Day</th>
              <th>Period</th>
              <th>Start</th>
              <th>End</th>
              <th>Subject</th>
              <th>Teacher</th>
              <th>Room</th>
              <th>Class</th>
              <th>Section</th>
            </tr>
          </thead>
          <tbody>
            {timetable.map((entry) => (
              <tr key={entry.id}>
                <td>{DAY_NAMES[entry.day_of_week]}</td>
                <td>{entry.period}</td>
                <td>{entry.start_time || '-'}</td>
                <td>{entry.end_time || '-'}</td>
                <td>{entry.subject_id}</td>
                <td>{entry.teacher_id}</td>
                <td>{entry.room_id || '-'}</td>
                <td>{entry.class_id}</td>
                <td>{entry.section_id || '-'}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </PageWrapper>
  )
}