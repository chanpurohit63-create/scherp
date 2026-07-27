import React, { useEffect, useState } from 'react'
import PageWrapper from '../components/PageWrapper'
import { useAuth } from '../hooks/useAuth'
import { listResources, createResource } from '../api'

export default function TeachersPage() {
  const auth = useAuth()
  const [teachers, setTeachers] = useState([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [form, setForm] = useState({ user_id: '', employee_no: '', hire_date: '', is_active: true })

  useEffect(() => {
    loadTeachers()
  }, [])

  const loadTeachers = async () => {
    setLoading(true)
    setError('')
    try {
      const data = await listResources(auth.token, 'teachers')
      setTeachers(data)
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
      await createResource(auth.token, 'teachers', {
        user_id: Number(form.user_id),
        employee_no: form.employee_no,
        hire_date: form.hire_date || undefined,
        is_active: form.is_active,
      })
      setForm({ user_id: '', employee_no: '', hire_date: '', is_active: true })
      await loadTeachers()
    } catch (err) {
      setError(err.message)
    }
  }

  return (
    <PageWrapper title="Teachers">
      <section style={{ marginBottom: 24 }}>
        <h2>Create Teacher</h2>
        <form onSubmit={handleCreate} style={{ display: 'grid', gap: 12, maxWidth: 520 }}>
          <input type="number" value={form.user_id} onChange={(e) => setForm({ ...form, user_id: e.target.value })} placeholder="User ID" required />
          <input value={form.employee_no} onChange={(e) => setForm({ ...form, employee_no: e.target.value })} placeholder="Employee number" />
          <input type="date" value={form.hire_date} onChange={(e) => setForm({ ...form, hire_date: e.target.value })} />
          <select value={form.is_active ? 'true' : 'false'} onChange={(e) => setForm({ ...form, is_active: e.target.value === 'true' })}>
            <option value="true">Active</option>
            <option value="false">Inactive</option>
          </select>
          <button type="submit" style={{ padding: '10px 16px' }}>Create</button>
        </form>
      </section>

      <section>
        <h2>Teacher List</h2>
        {loading ? (
          <p>Loading teachers...</p>
        ) : (
          <table style={{ width: '100%', borderCollapse: 'collapse' }}>
            <thead>
              <tr>
                <th style={thStyle}>ID</th>
                <th style={thStyle}>User ID</th>
                <th style={thStyle}>Employee No</th>
                <th style={thStyle}>Hire Date</th>
                <th style={thStyle}>Active</th>
              </tr>
            </thead>
            <tbody>
              {teachers.map((teacher) => (
                <tr key={teacher.id}>
                  <td style={tdStyle}>{teacher.id}</td>
                  <td style={tdStyle}>{teacher.user_id}</td>
                  <td style={tdStyle}>{teacher.employee_no}</td>
                  <td style={tdStyle}>{teacher.hire_date}</td>
                  <td style={tdStyle}>{String(teacher.is_active)}</td>
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
