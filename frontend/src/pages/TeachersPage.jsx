import React, { useEffect, useState } from 'react'
import PageWrapper from '../components/PageWrapper'
import { useAuth } from '../hooks/useAuth.jsx'
import { listResources, createResource, deleteResource } from '../api'
import toast from 'react-hot-toast'

export default function TeachersPage() {
  const auth = useAuth()
  const [teachers, setTeachers] = useState([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [form, setForm] = useState({ user_id: '', employee_no: '', hire_date: '', is_active: true })
  const [search, setSearch] = useState('')
  const [sortBy, setSortBy] = useState('id')
  const [order, setOrder] = useState('asc')
  const [page, setPage] = useState(0)
  const pageSize = 10

  useEffect(() => { loadTeachers() }, [page, search, sortBy, order])

  const buildQuery = () => {
    const params = new URLSearchParams({ skip: page * pageSize, limit: pageSize, sort_by: sortBy, order })
    if (search) params.set('query', search)
    return params.toString()
  }

  const loadTeachers = async () => {
    setLoading(true); setError('')
    try {
      const data = await listResources(auth.token, 'teachers', buildQuery())
      setTeachers(data)
    } catch (err) { setError(err.message) }
    finally { setLoading(false) }
  }

  const handleCreate = async (event) => {
    event.preventDefault(); setError('')
    const toastId = toast.loading('Creating teacher...')
    try {
      await createResource(auth.token, 'teachers', { user_id: Number(form.user_id), employee_no: form.employee_no, hire_date: form.hire_date || undefined, is_active: form.is_active })
      toast.success('Teacher created!', { id: toastId })
      setForm({ user_id: '', employee_no: '', hire_date: '', is_active: true })
      await loadTeachers()
    } catch (err) { setError(err.message); toast.error(err.message, { id: toastId }) }
  }

  const handleDelete = async (id) => {
    if (!window.confirm('Delete this teacher?')) return
    try { await deleteResource(auth.token, 'teachers', id); toast.success('Teacher deleted'); await loadTeachers() }
    catch (err) { toast.error(err.message) }
  }

  const toggleSort = (col) => {
    if (sortBy === col) setOrder(order === 'asc' ? 'desc' : 'asc')
    else { setSortBy(col); setOrder('asc') }
  }

  return (
    <PageWrapper title="Teachers">
      <div className="card" style={{ marginBottom: 24 }}>
        <h2>Create Teacher</h2>
        <form onSubmit={handleCreate} className="form-grid">
          <input className="input" type="number" value={form.user_id} onChange={(e) => setForm({ ...form, user_id: e.target.value })} placeholder="User ID" required />
          <input className="input" value={form.employee_no} onChange={(e) => setForm({ ...form, employee_no: e.target.value })} placeholder="Employee number" />
          <input className="input" type="date" value={form.hire_date} onChange={(e) => setForm({ ...form, hire_date: e.target.value })} />
          <select className="input" value={form.is_active ? 'true' : 'false'} onChange={(e) => setForm({ ...form, is_active: e.target.value === 'true' })}>
            <option value="true">Active</option><option value="false">Inactive</option>
          </select>
          <button className="btn btn-primary" type="submit">Create</button>
        </form>
      </div>
      <div className="card">
        <div className="list-header">
          <h2>Teacher List</h2>
          <input className="input search-input" placeholder="Search..." value={search} onChange={(e) => { setSearch(e.target.value); setPage(0) }} />
        </div>
        {loading ? (
          <div className="skeleton-list">{Array.from({ length: 5 }).map((_, i) => <div key={i} className="skeleton-row" />)}</div>
        ) : teachers.length === 0 ? (
          <div className="empty-state">No teachers found.</div>
        ) : (
          <div className="table-responsive">
            <table className="data-table">
              <thead><tr>
                <th onClick={() => toggleSort('id')} style={{ cursor: 'pointer' }}>ID {sortBy === 'id' && (order === 'asc' ? '↑' : '↓')}</th>
                <th>User ID</th><th>Employee No</th><th>Hire Date</th><th>Active</th><th>Actions</th>
              </tr></thead>
              <tbody>
                {teachers.map((t) => (
                  <tr key={t.id}>
                    <td>{t.id}</td><td>{t.user_id}</td><td>{t.employee_no}</td><td>{t.hire_date}</td>
                    <td><span className="role-badge">{String(t.is_active)}</span></td>
                    <td className="action-cell"><button className="btn btn-sm btn-danger" onClick={() => handleDelete(t.id)}>Delete</button></td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
        <div className="pagination">
          <button className="btn btn-sm" disabled={page === 0} onClick={() => setPage(page - 1)}>Previous</button>
          <span>Page {page + 1}</span>
          <button className="btn btn-sm" disabled={teachers.length < pageSize} onClick={() => setPage(page + 1)}>Next</button>
        </div>
      </div>
      {error && <div className="error-banner">{error}</div>}
    </PageWrapper>
  )
}
