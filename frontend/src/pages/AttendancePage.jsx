import React, { useEffect, useState } from 'react'
import PageWrapper from '../components/PageWrapper'
import { useAuth } from '../hooks/useAuth.jsx'
import { listResources, createResource } from '../api'
import toast from 'react-hot-toast'

export default function AttendancePage() {
  const auth = useAuth()
  const [attendance, setAttendance] = useState([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [form, setForm] = useState({ student_id: '', date: '', status: 'present', remarks: '' })
  const [search, setSearch] = useState('')
  const [page, setPage] = useState(0)
  const pageSize = 10

  useEffect(() => { loadAttendance() }, [page, search])

  const buildQuery = () => {
    const params = new URLSearchParams({ skip: page * pageSize, limit: pageSize })
    if (search) params.set('query', search)
    return params.toString()
  }

  const loadAttendance = async () => {
    setLoading(true); setError('')
    try { const data = await listResources(auth.token, 'attendances', buildQuery()); setAttendance(data) }
    catch (err) { setError(err.message) } finally { setLoading(false) }
  }

  const handleCreate = async (event) => {
    event.preventDefault(); setError('')
    const toastId = toast.loading('Recording attendance...')
    try {
      await createResource(auth.token, 'attendances', { student_id: Number(form.student_id), date: form.date, status: form.status, remarks: form.remarks })
      toast.success('Attendance recorded!', { id: toastId })
      setForm({ student_id: '', date: '', status: 'present', remarks: '' })
      await loadAttendance()
    } catch (err) { setError(err.message); toast.error(err.message, { id: toastId }) }
  }

  return (
    <PageWrapper title="Attendance">
      <div className="card" style={{ marginBottom: 24 }}>
        <h2>Record Attendance</h2>
        <form onSubmit={handleCreate} className="form-grid">
          <input className="input" type="number" value={form.student_id} onChange={(e) => setForm({ ...form, student_id: e.target.value })} placeholder="Student ID" required />
          <input className="input" type="date" value={form.date} onChange={(e) => setForm({ ...form, date: e.target.value })} required />
          <select className="input" value={form.status} onChange={(e) => setForm({ ...form, status: e.target.value })}>
            <option value="present">Present</option><option value="absent">Absent</option><option value="late">Late</option>
          </select>
          <input className="input" value={form.remarks} onChange={(e) => setForm({ ...form, remarks: e.target.value })} placeholder="Remarks" />
          <button className="btn btn-primary" type="submit">Record</button>
        </form>
      </div>
      <div className="card">
        <div className="list-header">
          <h2>Attendance Records</h2>
          <input className="input search-input" placeholder="Search..." value={search} onChange={(e) => { setSearch(e.target.value); setPage(0) }} />
        </div>
        {loading ? (
          <div className="skeleton-list">{Array.from({ length: 5 }).map((_, i) => <div key={i} className="skeleton-row" />)}</div>
        ) : attendance.length === 0 ? (
          <div className="empty-state">No attendance records found.</div>
        ) : (
          <div className="table-responsive">
            <table className="data-table">
              <thead><tr><th>ID</th><th>Student ID</th><th>Date</th><th>Status</th><th>Remarks</th></tr></thead>
              <tbody>
                {attendance.map((item) => (
                  <tr key={item.id}>
                    <td>{item.id}</td><td>{item.student_id}</td><td>{item.date}</td>
                    <td><span className="role-badge">{item.status}</span></td><td>{item.remarks}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
        <div className="pagination">
          <button className="btn btn-sm" disabled={page === 0} onClick={() => setPage(page - 1)}>Previous</button>
          <span>Page {page + 1}</span>
          <button className="btn btn-sm" disabled={attendance.length < pageSize} onClick={() => setPage(page + 1)}>Next</button>
        </div>
      </div>
      {error && <div className="error-banner">{error}</div>}
    </PageWrapper>
  )
}
