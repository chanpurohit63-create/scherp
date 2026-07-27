import React, { useEffect, useState } from 'react'
import PageWrapper from '../components/PageWrapper'
import { useAuth } from '../hooks/useAuth'
import { listResources, createResource, deleteResource } from '../api'

export default function StudentsPage() {
  const auth = useAuth()
  const [students, setStudents] = useState([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [form, setForm] = useState({ user_id: '', admission_no: '', gender: '', status: 'active' })

  useEffect(() => {
    loadStudents()
  }, [])

  const loadStudents = async () => {
    setLoading(true)
    setError('')
    try {
      const data = await listResources(auth.token, 'students')
      setStudents(data)
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  const handleCreate = async (event) => {
    event.preventDefault()
    setError('')
    try {
      await createResource(auth.token, 'students', {
        user_id: Number(form.user_id),
        admission_no: form.admission_no,
        gender: form.gender,
        status: form.status,
      })
      setForm({ user_id: '', admission_no: '', gender: '', status: 'active' })
      await loadStudents()
    } catch (err) {
      setError(err.message)
    }
  }

  return (
    <PageWrapper title="Students">
      <section style={{ marginBottom: 24 }}>
        <h2>Create Student</h2>
        <form onSubmit={handleCreate} style={{ display: 'grid', gap: 12, maxWidth: 520 }}>
          <input type="number" value={form.user_id} onChange={(e) => setForm({ ...form, user_id: e.target.value })} placeholder="User ID" required />
          <input value={form.admission_no} onChange={(e) => setForm({ ...form, admission_no: e.target.value })} placeholder="Admission number" />
          <input value={form.gender} onChange={(e) => setForm({ ...form, gender: e.target.value })} placeholder="Gender" />
          <select value={form.status} onChange={(e) => setForm({ ...form, status: e.target.value })}>
            <option value="active">Active</option>
            <option value="inactive">Inactive</option>
          </select>
          <button type="submit" style={{ padding: '10px 16px' }}>Create</button>
        </form>
      </section>

      <section>
        <h2>Student List</h2>
        {loading ? (
          <p>Loading students...</p>
        ) : (
          <table style={{ width: '100%', borderCollapse: 'collapse' }}>
            <thead>
              <tr>
                <th style={thStyle}>ID</th>
                <th style={thStyle}>User ID</th>
                <th style={thStyle}>Admission</th>
                <th style={thStyle}>Gender</th>
                <th style={thStyle}>Status</th>
              </tr>
            </thead>
            <tbody>
              {students.map((student) => (
                <tr key={student.id}>
                  <td style={tdStyle}>{student.id}</td>
                  <td style={tdStyle}>{student.user_id}</td>
                  <td style={tdStyle}>{student.admission_no}</td>
                  <td style={tdStyle}>{student.gender}</td>
                  <td style={tdStyle}>{student.status}</td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </section>
      {error && <p style={{ color: 'red' }}>{error}</p>}
    </PageWrapper>
  )
}

const thStyle = { borderBottom: '1px solid #ddd', padding: 8, textAlign: 'left' }
const tdStyle = { borderBottom: '1px solid #eee', padding: 8 }
