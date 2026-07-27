import React, { useEffect, useState } from 'react'
import PageWrapper from '../components/PageWrapper'
import { useAuth } from '../hooks/useAuth.jsx'
import { listResources, createResource, updateResource, deleteResource } from '../api'
import toast from 'react-hot-toast'

export default function EventsPage() {
  const auth = useAuth()
  const [items, setItems] = useState([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [search, setSearch] = useState('')
  const [page, setPage] = useState(0)
  const [editing, setEditing] = useState(null)
  const [form, setForm] = useState({ title: '', description: '', start_date: '', end_date: '', event_type: '', target_roles: '' })
  const limit = 20

  useEffect(() => { load() }, [page, search])

  const load = async () => {
    setLoading(true); setError('')
    try {
      const q = `skip=${page * limit}&limit=${limit}${search ? `&query=${search}` : ''}`
      setItems(await listResources(auth.token, 'events', q))
    } catch (err) { setError(err.message) } finally { setLoading(false) }
  }

  const handleSubmit = async (e) => {
    e.preventDefault(); setError('')
    const toastId = toast.loading(editing ? 'Updating...' : 'Creating...')
    try {
      const body = { ...form, start_date: form.start_date ? new Date(form.start_date).toISOString() : undefined, end_date: form.end_date ? new Date(form.end_date).toISOString() : undefined }
      if (editing) { await updateResource(auth.token, 'events', editing, body); toast.success('Updated!', { id: toastId }) }
      else { await createResource(auth.token, 'events', body); toast.success('Created!', { id: toastId }) }
      setForm({ title: '', description: '', start_date: '', end_date: '', event_type: '', target_roles: '' }); setEditing(null); await load()
    } catch (err) { setError(err.message); toast.error(err.message, { id: toastId }) }
  }

  const handleEdit = (item) => {
    setEditing(item.id)
    setForm({ title: item.title, description: item.description || '', start_date: item.start_date ? item.start_date.slice(0, 16) : '', end_date: item.end_date ? item.end_date.slice(0, 16) : '', event_type: item.event_type || '', target_roles: item.target_roles || '' })
  }
  const handleDelete = async (id) => {
    if (!window.confirm('Delete this event?')) return
    try { await deleteResource(auth.token, 'events', id); toast.success('Deleted'); await load() }
    catch (err) { toast.error(err.message) }
  }

  return (
    <PageWrapper title="Events">
      <div className="card" style={{ marginBottom: 24 }}>
        <h2>{editing ? 'Edit' : 'Create'} Event</h2>
        <form onSubmit={handleSubmit} className="form-grid">
          <input className="input" value={form.title} onChange={(e) => setForm({ ...form, title: e.target.value })} placeholder="Title" required />
          <textarea className="input" value={form.description} onChange={(e) => setForm({ ...form, description: e.target.value })} placeholder="Description" rows={3} />
          <input className="input" type="datetime-local" value={form.start_date} onChange={(e) => setForm({ ...form, start_date: e.target.value })} required />
          <input className="input" type="datetime-local" value={form.end_date} onChange={(e) => setForm({ ...form, end_date: e.target.value })} required />
          <input className="input" value={form.event_type} onChange={(e) => setForm({ ...form, event_type: e.target.value })} placeholder="Event type (e.g. Holiday, Exam, Meeting)" />
          <input className="input" value={form.target_roles} onChange={(e) => setForm({ ...form, target_roles: e.target.value })} placeholder="Target roles (comma-separated)" />
          <div className="form-actions">
            <button className="btn btn-primary" type="submit">{editing ? 'Update' : 'Create'}</button>
            {editing && <button className="btn" type="button" onClick={() => { setEditing(null); setForm({ title: '', description: '', start_date: '', end_date: '', event_type: '', target_roles: '' }) }}>Cancel</button>}
          </div>
        </form>
      </div>
      <div className="card">
        <div className="filter-bar"><input className="input" placeholder="Search events..." value={search} onChange={(e) => { setSearch(e.target.value); setPage(0) }} /></div>
        {loading ? <div className="skeleton-list">{Array.from({ length: 5 }).map((_, i) => <div key={i} className="skeleton-row" />)}</div>
        : items.length === 0 ? <div className="empty-state">No events found.</div>
        : <div className="table-responsive">
            <table className="data-table">
              <thead><tr><th>ID</th><th>Title</th><th>Type</th><th>Start</th><th>End</th><th>Target Roles</th><th>Actions</th></tr></thead>
              <tbody>
                {items.map((item) => (
                  <tr key={item.id}>
                    <td>{item.id}</td><td>{item.title}</td><td>{item.event_type || '-'}</td>
                    <td>{new Date(item.start_date).toLocaleString()}</td><td>{new Date(item.end_date).toLocaleString()}</td>
                    <td>{item.target_roles || 'All'}</td>
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
