import React, { useEffect, useState } from 'react'
import PageWrapper from '../components/PageWrapper'
import { useAuth } from '../hooks/useAuth.jsx'
import { listResources, createResource, updateResource, deleteResource } from '../api'
import toast from 'react-hot-toast'

export default function ClassesPage() {
  const auth = useAuth()
  const [items, setItems] = useState([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [search, setSearch] = useState('')
  const [page, setPage] = useState(0)
  const [editing, setEditing] = useState(null)
  const [form, setForm] = useState({ name: '', grade_level: '' })
  const limit = 20

  useEffect(() => { load() }, [page, search])

  const load = async () => {
    setLoading(true); setError('')
    try {
      const q = `skip=${page * limit}&limit=${limit}${search ? `&query=${search}` : ''}`
      setItems(await listResources(auth.token, 'classes', q))
    } catch (err) { setError(err.message) } finally { setLoading(false) }
  }

  const handleSubmit = async (e) => {
    e.preventDefault(); setError('')
    const toastId = toast.loading(editing ? 'Updating...' : 'Creating...')
    try {
      if (editing) { await updateResource(auth.token, 'classes', editing, form); toast.success('Updated!', { id: toastId }) }
      else { await createResource(auth.token, 'classes', form); toast.success('Created!', { id: toastId }) }
      setForm({ name: '', grade_level: '' }); setEditing(null); await load()
    } catch (err) { setError(err.message); toast.error(err.message, { id: toastId }) }
  }

  const handleEdit = (item) => { setEditing(item.id); setForm({ name: item.name, grade_level: item.grade_level || '' }) }
  const handleDelete = async (id) => {
    if (!window.confirm('Delete this class?')) return
    try { await deleteResource(auth.token, 'classes', id); toast.success('Deleted'); await load() }
    catch (err) { toast.error(err.message) }
  }

  return (
    <PageWrapper title="Classes">
      <div className="card" style={{ marginBottom: 24 }}>
        <h2>{editing ? 'Edit' : 'Create'} Class</h2>
        <form onSubmit={handleSubmit} className="form-grid">
          <input className="input" value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} placeholder="Class name" required />
          <input className="input" value={form.grade_level} onChange={(e) => setForm({ ...form, grade_level: e.target.value })} placeholder="Grade level" />
          <div className="form-actions">
            <button className="btn btn-primary" type="submit">{editing ? 'Update' : 'Create'}</button>
            {editing && <button className="btn" type="button" onClick={() => { setEditing(null); setForm({ name: '', grade_level: '' }) }}>Cancel</button>}
          </div>
        </form>
      </div>
      <div className="card">
        <div className="filter-bar"><input className="input" placeholder="Search classes..." value={search} onChange={(e) => { setSearch(e.target.value); setPage(0) }} /></div>
        {loading ? <div className="skeleton-list">{Array.from({ length: 5 }).map((_, i) => <div key={i} className="skeleton-row" />)}</div>
        : items.length === 0 ? <div className="empty-state">No classes found.</div>
        : <div className="table-responsive">
            <table className="data-table">
              <thead><tr><th>ID</th><th>Name</th><th>Grade Level</th><th>Actions</th></tr></thead>
              <tbody>
                {items.map((item) => (
                  <tr key={item.id}>
                    <td>{item.id}</td><td>{item.name}</td><td>{item.grade_level || '-'}</td>
                    <td className="action-cell">
                      <button className="btn btn-sm" onClick={() => handleEdit(item)}>Edit</button>
                      <button className="btn btn-sm btn-danger" onClick={() => handleDelete(item.id)}>Delete</button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>}
        <div className="pagination">
          <button className="btn btn-sm" disabled={page === 0} onClick={() => setPage(page - 1)}>Previous</button>
          <span>Page {page + 1}</span>
          <button className="btn btn-sm" disabled={items.length < limit} onClick={() => setPage(page + 1)}>Next</button>
        </div>
      </div>
      {error && <div className="error-banner">{error}</div>}
    </PageWrapper>
  )
}
