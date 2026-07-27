import React, { useEffect, useState } from 'react'
import TeacherLayout from '../components/TeacherLayout'
import { useAuth } from '../hooks/useAuth.jsx'
import { listResources, createResource } from '../api'
import toast from 'react-hot-toast'

export default function TeacherAttendancePage() {
  const auth = useAuth()
  const [classes, setClasses] = useState([])
  const [students, setStudents] = useState([])
  const [selectedClass, setSelectedClass] = useState('')
  const [attendanceDate, setAttendanceDate] = useState(new Date().toISOString().split('T')[0])
  const [attendanceData, setAttendanceData] = useState({})
  const [loading, setLoading] = useState(true)

  useEffect(() => { loadClasses() }, [])

  const loadClasses = async () => {
    try {
      const d = await listResources(auth.token, 'portal/teacher/classes')
      setClasses(d || [])
    } catch (err) { console.error(err) }
    finally { setLoading(false) }
  }

  const loadStudents = async (classId) => {
    try {
      const d = await listResources(auth.token, `portal/teacher/classes/${classId}/students`)
      setStudents(d || [])
      const att = {}
      ;(d || []).forEach(({ student }) => { att[student.id] = 'present' })
      setAttendanceData(att)
    } catch (err) { console.error(err) }
  }

  const handleMarkAll = (status) => {
    const newAtt = {}
    students.forEach(({ student }) => { newAtt[student.id] = status })
    setAttendanceData(newAtt)
  }

  const handleSave = async () => {
    try {
      for (const [studentId, status] of Object.entries(attendanceData)) {
        await createResource(auth.token, 'portal/teacher/attendance', {
          student_id: parseInt(studentId),
          date: attendanceDate,
          status
        })
      }
      toast.success('Attendance saved')
    } catch (err) { toast.error('Save failed') }
  }

  if (loading) {
    return <TeacherLayout title="Attendance"><div className="skeleton-card" style={{ height: 200 }} /></TeacherLayout>
  }

  return (
    <TeacherLayout title="Attendance">
      <div className="filter-bar">
        <select className="input" value={selectedClass} onChange={(e) => { setSelectedClass(e.target.value); if (e.target.value) loadStudents(parseInt(e.target.value)) }}>
          <option value="">Select class</option>
          {classes.map((item) => (
            <option key={item.allocation.id} value={item.class.id}>{item.class.name} - {item.subject.name}</option>
          ))}
        </select>
        <input className="input" type="date" value={attendanceDate} onChange={(e) => setAttendanceDate(e.target.value)} />
        <div className="action-cell">
          <button className="btn btn-sm" onClick={() => handleMarkAll('present')}>All Present</button>
          <button className="btn btn-sm" onClick={() => handleMarkAll('absent')}>All Absent</button>
          <button className="btn btn-primary btn-sm" onClick={handleSave}>Save</button>
        </div>
      </div>

      {students.length > 0 && (
        <div className="card">
          <h3>Mark Attendance</h3>
          <div className="table-responsive">
            <table className="data-table">
              <thead><tr><th>Student</th><th>Present</th><th>Absent</th><th>Leave</th></tr></thead>
              <tbody>
                {students.map(({ student, user }) => (
                  <tr key={student.id}>
                    <td><strong>{user?.full_name || '-'}</strong> ({student.admission_no})</td>
                    <td><input type="radio" name={`att_${student.id}`} checked={attendanceData[student.id] === 'present'} onChange={() => setAttendanceData(prev => ({ ...prev, [student.id]: 'present' }))} /></td>
                    <td><input type="radio" name={`att_${student.id}`} checked={attendanceData[student.id] === 'absent'} onChange={() => setAttendanceData(prev => ({ ...prev, [student.id]: 'absent' }))} /></td>
<td><input type="radio" name={`att_${student.id}`} checked={attendanceData[student.id] === 'leave'} onChange={() => setAttendanceData(prev => ({ ...prev, [student.id]: 'leave' }))} /></td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
      {students.length === 0 && selectedClass && <div className="empty-state">No students found</div>}
    </TeacherLayout>
  )
}
