import React, { useEffect, useState } from 'react'
import PageWrapper from '../components/PageWrapper'
import { useAuth } from '../hooks/useAuth.jsx'
import { listResources, getBackendUrl } from '../api'

const DAY_NAMES = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']

export default function ClassTimetablePage() {
  const auth = useAuth()
  const [timetable, setTimetable] = useState([])
  const [loading, setLoading] = useState(true)
  const [classId, setClassId] = useState('')
  const [academicYearId, setAcademicYearId] = useState('')

  useEffect(() => {
    loadTimetable()
  }, [])

  const loadTimetable = async () => {
    try {
      const cid = classId || auth.profile?.id
      const params = new URLSearchParams()
      if (academicYearId) params.set('academic_year_id', academicYearId)
      const data = await listResources(auth.token, `classes/${cid}/timetable?${params.toString()}`)
      setTimetable(data)
    } catch (err) {
      console.error(err)
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return (
      <PageWrapper title="Class Timetable">
        <div className="skeleton-grid">
          {Array.from({ length: 4 }).map((_, i) => <div key={i} className="skeleton-card" />)}
        </div>
      </PageWrapper>
    )
  }

  return (
    <PageWrapper title="Class Timetable">
      <div className="flex gap-4 mb-6 flex-wrap">
        <div className="form-group">
          <label>Class ID</label>
          <input type="number" value={classId} onChange={(e) => setClassId(e.target.value)} className="input" />
        </div>
        <div className="form-group">
          <label>Academic Year</label>
          <input type="number" value={academicYearId} onChange={(e) => setAcademicYearId(e.target.value)} className="input" />
        </div>
        <button onClick={loadTimetable} className="btn btn-primary">Apply</button>
      </div>

      <h3 className="card-title">Class Schedule</h3>
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
              <th>Section</th>
              <th>Room</th>
              <th>Status</th>
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