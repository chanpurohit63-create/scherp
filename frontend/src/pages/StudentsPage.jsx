import React, { useEffect, useState } from 'react'
import PageWrapper from '../components/PageWrapper'
import { useAuth } from '../hooks/useAuth.jsx'
import { listResources, createResource, deleteResource } from '../api'
import toast from 'react-hot-toast'

export default function StudentsPage() {
  const auth = useAuth()
  const [students, setStudents] = useState([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [form, setForm] = useState({ user_id: '', admission_no: '', gender: '', status: 'active' })
  const [search, setSearch] = useState('')
  const [sortBy, setSortBy] = useState('id')
  const [order, setOrder] = useState('asc')
  const [page, setPage] = useState(0)
  const pageSize = 10

  useEffect(() => {
    loadStudents()
  }, [page, search, sortBy, order])

  const buildQuery = () => {
    const params = new URLSearchParams({ skip: page * pageSize, limit: pageSize, sort_by: sortBy, order })
    if (search) params.set('query', search)
    return params.toString()
  }

  const loadStudents = async () => {
    setLoading(true)
    setError('')
    try {
      const data = await listResources(auth.token, 'students', buildQuery())
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
    const toastId = toast.loading('Creating student...')
    try {
      await createResource(auth.token, 'students', {
        user_id: Number(form.user_id),
        admission_no: form.admission_no,
        gender: form.gender,
        status: form.status,
      })
      toast.success('Student created!', { id: toastId })
      setForm({ user_id: '', admission_no: '', gender: '', status: 'active' })
      await loadStudents()
    } catch (err) {
      setError(err.message)
      toast.error(err.message, { id: toastId })
    }
  }

  const handleDelete = async (id) => {
    if (!window.confirm('Delete this student?')) return
    try {
      await deleteResource(auth.token, 'students', id)
      toast.success('Student deleted')
      await loadStudents()
    } catch (err) {
      toast.error(err.message)
    }
  }

  const toggleSort = (col) => {
    if (sortBy === col) setOrder(order === 'asc' ? 'desc' : 'asc')
    else { setSortBy(col); setOrder('asc') }
  }

  return (
    <PageWrapper title="Students">
      <div className="card" style={{ marginBottom: 24 }}>
        <h2>Create Student</h2>
        <form onSubmit={handleCreate} className="form-grid">
          <input className="input" type="number" value={form.user_id} onChange={(e) => setForm({ ...form, user_id: e.target.value })} placeholder="User ID" required />
          <input className="input" value={form.admission_no} onChange={(e) => setForm({ ...form, admission_no: e.target.value })} placeholder="Admission number" />
          <input className="input" value={form.gender} onChange={(e) => setForm({ ...form, gender: e.target.value })} placeholder="Gender" />
          <select className="input" value={form.status} onChange={(e) => setForm({ ...form, status: e.target.value })}>
            <option value="active">Active</option>
            <option value="inactive">Inactive</option>
          </select>
          <button className="btn btn-primary" type="submit">Create</button>
        </form>
      </div>

      <div className="card">
        <div className="list-header">
          <h2>Student List</h2>
          <input className="input search-input" placeholder="Search..." value={search} onChange={(e) => { setSearch(e.target.value); setPage(0) }} />
        </div>
        {loading ? (
          <div className="skeleton-list">{Array.from({ length: 5 }).map((_, i) => <div key={i} className="skeleton-row" />)}</div>
        ) : students.length === 0 ? (
          <div className="empty-state">No students found.</div>
        ) : (
          <div className="table-responsive">
            <table className="data-table">
              <thead>
                <tr>
                  <th onClick={() => toggleSort('id')} style={{ cursor: 'pointer' }}>ID {sortBy === 'id' && (order === 'asc' ? '↑' : '↓')}</th>
                  <th>User ID</th>
                  <th>Admission</th>
                  <th>Gender</th>
                  <th>Status</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                {students.map((student) => (
                  <tr key={student.id}>
                    <td>{student.id}</td>
                    <td>{student.user_id}</td>
                    <td>{student.admission_no}</td>
                    <td>{student.gender}</td>
                    <td><span className="role-badge">{student.status}</span></td>
                    <td className="action-cell">
                      <button className="btn btn-sm btn-danger" onClick={() => handleDelete(student.id)}>Delete</button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
        <div className="pagination">
          <button className="btn btn-sm" disabled={page === 0} onClick={() => setPage(page - 1)}>Previous</button>
          <span>Page {page + 1}</span>
          <button className="btn btn-sm" disabled={students.length < pageSize} onClick={() => setPage(page + 1)}>Next</button>
        </div>
      </div>
      {error && <div className="error-banner">{error}</div>}
    </PageWrapper>
  )
}
