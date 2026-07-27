import React, { useEffect, useState } from 'react'
import PageWrapper from '../components/PageWrapper'
import { useAuth } from '../hooks/useAuth'
import { listResources, createResource } from '../api'

export default function AttendancePage() {
  const auth = useAuth()
  const [attendance, setAttendance] = useState([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [form, setForm] = useState({ student_id: '', date: '', status: 'present', remarks: '' })

  useEffect(() => {
    loadAttendance()
  }, [])

  const loadAttendance = async () => {
    setLoading(true)
    setError('')
    try {
      const data = await listResources(auth.token, 'attendances')
      setAttendance(data)
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
      await createResource(auth.token, 'attendances', {
        student_id: Number(form.student_id),
        date: form.date,
        status: form.status,
        remarks: form.remarks,
      })
      setForm({ student_id: '', date: '', status: 'present', remarks: '' })
      await loadAttendance()
    } catch (err) {
      setError(err.message)
    }
  }

  return (
    <PageWrapper title="Attendance">
      <section style={{ marginBottom: 24 }}>
        <h2>Record Attendance</h2>
        <form onSubmit={handleCreate} style={{ display: 'grid', gap: 12, maxWidth: 520 }}>
          <input type="number" value={form.student_id} onChange={(e) => setForm({ ...form, student_id: e.target.value })} placeholder="Student ID" required />
          <input type="date" value={form.date} onChange={(e) => setForm({ ...form, date: e.target.value })} required />
          <select value={form.status} onChange={(e) => setForm({ ...form, status: e.target.value })}>
            <option value="present">Present</option>
            <option value="absent">Absent</option>
            <option value="late">Late</option>
          </select>
          <input value={form.remarks} onChange={(e) => setForm({ ...form, remarks: e.target.value })} placeholder="Remarks" />
          <button type="submit" style={{ padding: '10px 16px' }}>Record</button>
        </form>
      </section>

      <section>
        <h2>Attendance Records</h2>
        {loading ? (
          <p>Loading attendance...</p>
        ) : (
          <table style={{ width: '100%', borderCollapse: 'collapse' }}>
            <thead>
              <tr>
                <th style={thStyle}>ID</th>
                <th style={thStyle}>Student ID</th>
                <th style={thStyle}>Date</th>
                <th style={thStyle}>Status</th>
                <th style={thStyle}>Remarks</th>
              </tr>
            </thead>
            <tbody>
              {attendance.map((item) => (
                <tr key={item.id}>
                  <td style={tdStyle}>{item.id}</td>
                  <td style={tdStyle}>{item.student_id}</td>
                  <td style={tdStyle}>{item.date}</td>
                  <td style={tdStyle}>{item.status}</td>
                  <td style={tdStyle}>{item.remarks}</td>
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
