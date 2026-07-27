import React, { useEffect, useState } from 'react'
import PageWrapper from '../components/PageWrapper'
import { useAuth } from '../hooks/useAuth.jsx'
import { listResources, createResource, updateResource, deleteResource } from '../api'
import toast from 'react-hot-toast'

export default function SectionsPage() {
  const auth = useAuth()
  const [items, setItems] = useState([])
  const [classes, setClasses] = useState([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [page, setPage] = useState(0)
  const [editing, setEditing] = useState(null)
  const [form, setForm] = useState({ name: '', class_id: '' })
  const limit = 20

  useEffect(() => { load(); loadClasses() }, [page])

  const load = async () => {
    setLoading(true); setError('')
    try { setItems(await listResources(auth.token, 'sections', `skip=${page * limit}&limit=${limit}`)) }
    catch (err) { setError(err.message) } finally { setLoading(false) }
  }
  const loadClasses = async () => { try { setClasses(await listResources(auth.token, 'classes')) } catch {} }

  const handleSubmit = async (e) => {
    e.preventDefault(); setError('')
    const toastId = toast.loading(editing ? 'Updating...' : 'Creating...')
    try {
      const body = { name: form.name, class_id: Number(form.class_id) }
      if (editing) { await updateResource(auth.token, 'sections', editing, body); toast.success('Updated!', { id: toastId }) }
      else { await createResource(auth.token, 'sections', body); toast.success('Created!', { id: toastId }) }
      setForm({ name: '', class_id: '' }); setEditing(null); await load()
    } catch (err) { setError(err.message); toast.error(err.message, { id: toastId }) }
  }

  const handleEdit = (item) => { setEditing(item.id); setForm({ name: item.name, class_id: item.class_id }) }
  const handleDelete = async (id) => {
    if (!window.confirm('Delete this section?')) return
    try { await deleteResource(auth.token, 'sections', id); toast.success('Deleted'); await load() }
    catch (err) { toast.error(err.message) }
  }

  return (
    <PageWrapper title="Sections">
      <div className="card" style={{ marginBottom: 24 }}>
        <h2>{editing ? 'Edit' : 'Create'} Section</h2>
        <form onSubmit={handleSubmit} className="form-grid">
          <input className="input" value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} placeholder="Section name" required />
          <select className="input" value={form.class_id} onChange={(e) => setForm({ ...form, class_id: e.target.value })} required>
            <option value="">Select Class</option>
            {classes.map((c) => <option key={c.id} value={c.id}>{c.name}</option>)}
          </select>
          <div className="form-actions">
            <button className="btn btn-primary" type="submit">{editing ? 'Update' : 'Create'}</button>
            {editing && <button className="btn" type="button" onClick={() => { setEditing(null); setForm({ name: '', class_id: '' }) }}>Cancel</button>}
          </div>
        </form>
      </div>
      <div className="card">
        <h2>Sections</h2>
        {loading ? <div className="skeleton-list">{Array.from({ length: 5 }).map((_, i) => <div key={i} className="skeleton-row" />)}</div>
        : items.length === 0 ? <div className="empty-state">No sections found.</div>
        : <div className="table-responsive">
            <table className="data-table">
              <thead><tr><th>ID</th><th>Name</th><th>Class ID</th><th>Actions</th></tr></thead>
              <tbody>
                {items.map((item) => (
                  <tr key={item.id}>
                    <td>{item.id}</td><td>{item.name}</td><td>{item.class_id}</td>
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
