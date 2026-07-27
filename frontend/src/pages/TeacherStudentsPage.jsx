import React, { useEffect, useState } from 'react'
import TeacherLayout from '../components/TeacherLayout'
import { useAuth } from '../hooks/useAuth.jsx'
import { listResources } from '../api'

export default function TeacherStudentsPage() {
  const auth = useAuth()
  const [classes, setClasses] = useState([])
  const [students, setStudents] = useState([])
  const [selectedClass, setSelectedClass] = useState('')
  const [search, setSearch] = useState('')
  const [selectedStudent, setSelectedStudent] = useState(null)
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
    } catch (err) { console.error(err) }
  }

  useEffect(() => {
    if (selectedClass) loadStudents(parseInt(selectedClass))
  }, [selectedClass])

  const filtered = students.filter(({ student, user }) => {
    if (!search) return true
    const q = search.toLowerCase()
    return (user?.full_name || '').toLowerCase().includes(q) || (student.admission_no || '').toLowerCase().includes(q)
  })

  if (loading) {
    return <TeacherLayout title="Students"><div className="skeleton-card" style={{ height: 200 }} /></TeacherLayout>
  }

  return (
    <TeacherLayout title="Students">
      <div className="filter-bar">
        <select className="input" value={selectedClass} onChange={(e) => setSelectedClass(e.target.value)}>
          <option value="">Select class</option>
          {classes.map((item) => (
            <option key={item.allocation.id} value={item.class.id}>{item.class.name} - {item.subject.name}</option>
          ))}
        </select>
        <input className="input search-input" placeholder="Search..." value={search} onChange={(e) => setSearch(e.target.value)} />
      </div>

      {selectedStudent ? (
        <div className="card">
          <div className="list-header">
            <h3>{selectedStudent.user?.full_name} - Profile</h3>
            <button className="btn" onClick={() => setSelectedStudent(null)}>Back</button>
          </div>
          <div className="form-grid">
            <label>Name <input className="input" value={selectedStudent.user?.full_name || ''} readOnly /></label>
            <label>Email <input className="input" value={selectedStudent.user?.email || ''} readOnly /></label>
            <label>Admission No <input className="input" value={selectedStudent.student.admission_no || ''} readOnly /></label>
            <label>Status <input className="input" value={selectedStudent.student.status || ''} readOnly /></label>
          </div>
        </div>
      ) : (
        <div className="card">
          <h3>Student List ({filtered.length})</h3>
          {filtered.length === 0 && <div className="empty-state">No students</div>}
          <div className="table-responsive">
            <table className="data-table">
              <thead><tr><th>Name</th><th>Admission No</th><th>Actions</th></tr></thead>
              <tbody>
                {filtered.map(({ student, user }) => (
                  <tr key={student.id}>
                    <td>{user?.full_name || '-'}</td>
                    <td>{student.admission_no || '-'}</td>
                    <td><button className="btn btn-sm" onClick={() => setSelectedStudent({ student, user })}>View</button></td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </TeacherLayout>
  )
}

