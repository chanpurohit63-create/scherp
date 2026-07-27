import React, { useEffect, useState } from 'react'
import TeacherLayout from '../components/TeacherLayout'
import { useAuth } from '../hooks/useAuth.jsx'
import { listResources } from '../api'

export default function TeacherClassesPage() {
  const auth = useAuth()
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(true)
  const [selectedClass, setSelectedClass] = useState(null)
  const [students, setStudents] = useState([])
  const [search, setSearch] = useState('')

  useEffect(() => { loadClasses() }, [])

  const loadClasses = async () => {
    try {
      const d = await listResources(auth.token, 'portal/teacher/classes')
      setData(d)
    } catch (err) { console.error(err) }
    finally { setLoading(false) }
  }

  const loadStudents = async (classId) => {
    try {
      const params = new URLSearchParams()
      if (search) params.set('search', search)
      const d = await listResources(auth.token, `portal/teacher/classes/${classId}/students`, params.toString())
      setStudents(d)
      setSelectedClass(classId)
    } catch (err) { console.error(err) }
  }

  if (loading) {
    return <TeacherLayout title="My Classes"><div className="skeleton-list"><div className="skeleton-row" /></div></TeacherLayout>
  }

  return (
    <TeacherLayout title="My Classes">
      <div className="filter-bar">
        <select className="input" onChange={(e) => { if (e.target.value) loadStudents(parseInt(e.target.value)) }}>
          <option value="">Select a class...</option>
          {(data || []).map((item) => (
            <option key={item.allocation.id} value={item.class.id}>{item.class.name} - {item.subject.name} {item.section ? `(${item.section.name})` : ''}</option>
          ))}
        </select>
        <input className="input search-input" placeholder="Search students..." value={search} onChange={(e) => setSearch(e.target.value)} />
        <button className="btn btn-primary btn-sm" onClick={() => selectedClass && loadStudents(selectedClass)}>Search</button>
      </div>

      {selectedClass && (
        <div className="card">
          <h3>Students</h3>
          <div className="table-responsive">
            <table className="data-table">
              <thead><tr><th>Name</th><th>Admission No</th><th>Email</th><th>Actions</th></tr></thead>
              <tbody>
                {students.map(({ student, user }) => (
                  <tr key={student.id}>
                    <td><strong>{user?.full_name || '-'}</strong></td>
                    <td>{student.admission_no || '-'}</td>
                    <td>{user?.email || '-'}</td>
                    <td className="action-cell">
                      <a href={`/teacher/students?studentId=${student.id}`} className="btn btn-sm">View</a>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          {students.length === 0 && <div className="empty-state">No students found</div>}
        </div>
      )}
    </TeacherLayout>
  )
}
