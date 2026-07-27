import React, { useEffect, useState } from 'react'
import PageWrapper from '../components/PageWrapper'
import { useAuth } from '../hooks/useAuth.jsx'
import { listResources, createResource, updateResource, deleteResource } from '../api'
import toast from 'react-hot-toast'

export default function AcademicYearsPage() {
  const auth = useAuth()
  const [items, setItems] = useState([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [editing, setEditing] = useState(null)
  const [form, setForm] = useState({ name: '', start_date: '', end_date: '', is_active: false })

  useEffect(() => { load() }, [])

  const load = async () => {
    setLoading(true); setError('')
    try { setItems(await listResources(auth.token, 'academic-years')) }
    catch (err) { setError(err.message) } finally { setLoading(false) }
  }

  const handleSubmit = async (e) => {
    e.preventDefault(); setError('')
    const toastId = toast.loading(editing ? 'Updating...' : 'Creating...')
    try {
      const body = { ...form, is_active: form.is_active === true || form.is_active === 'true' }
      if (editing) {
        await updateResource(auth.token, 'academic-years', editing, body)
        toast.success('Updated!', { id: toastId })
      } else {
        await createResource(auth.token, 'academic-years', body)
        toast.success('Created!', { id: toastId })
      }
      setForm({ name: '', start_date: '', end_date: '', is_active: false })
      setEditing(null)
      await load()
    } catch (err) { setError(err.message); toast.error(err.message, { id: toastId }) }
  }

  const handleEdit = (item) => {
    setEditing(item.id)
    setForm({ name: item.name, start_date: item.start_date, end_date: item.end_date, is_active: item.is_active })
  }

  const handleDelete = async (id) => {
    if (!window.confirm('Delete this academic year?')) return
    try { await deleteResource(auth.token, 'academic-years', id); toast.success('Deleted'); await load() }
    catch (err) { toast.error(err.message) }
  }

  return (
    <PageWrapper title="Academic Years">
      <div className="card" style={{ marginBottom: 24 }}>
        <h2>{editing ? 'Edit' : 'Create'} Academic Year</h2>
        <form onSubmit={handleSubmit} className="form-grid">
          <input className="input" value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} placeholder="Name (e.g. 2024-2025)" required />
          <input className="input" type="date" value={form.start_date} onChange={(e) => setForm({ ...form, start_date: e.target.value })} required />
          <input className="input" type="date" value={form.end_date} onChange={(e) => setForm({ ...form, end_date: e.target.value })} required />
          <label><input type="checkbox" checked={form.is_active === true || form.is_active === 'true'} onChange={(e) => setForm({ ...form, is_active: e.target.checked })} /> Active</label>
          <div className="form-actions">
            <button className="btn btn-primary" type="submit">{editing ? 'Update' : 'Create'}</button>
            {editing && <button className="btn" type="button" onClick={() => { setEditing(null); setForm({ name: '', start_date: '', end_date: '', is_active: false }) }}>Cancel</button>}
          </div>
        </form>
      </div>
      <div className="card">
        <h2>Academic Years</h2>
        {loading ? <div className="skeleton-list">{Array.from({ length: 3 }).map((_, i) => <div key={i} className="skeleton-row" />)}</div>
        : items.length === 0 ? <div className="empty-state">No academic years found.</div>
        : <div className="table-responsive">
            <table className="data-table">
              <thead><tr><th>ID</th><th>Name</th><th>Start</th><th>End</th><th>Active</th><th>Actions</th></tr></thead>
              <tbody>
                {items.map((item) => (
                  <tr key={item.id}>
                    <td>{item.id}</td><td>{item.name}</td><td>{item.start_date}</td><td>{item.end_date}</td>
                    <td><span className="role-badge">{item.is_active ? 'Yes' : 'No'}</span></td>
                    <td className="action-cell">
                      <button className="btn btn-sm" onClick={() => handleEdit(item)}>Edit</button>
                      <button className="btn btn-sm btn-danger" onClick={() => handleDelete(item.id)}>Delete</button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>}
      </div>
      {error && <div className="error-banner">{error}</div>}
    </PageWrapper>
  )
}

