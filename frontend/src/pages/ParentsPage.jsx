import React, { useEffect, useState } from 'react'
import PageWrapper from '../components/PageWrapper'
import { useAuth } from '../hooks/useAuth.jsx'
import { listResources, createResource, getResource, deleteResource } from '../api'
import toast from 'react-hot-toast'

export default function ParentsPage() {
  const auth = useAuth()
  const [items, setItems] = useState([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [page, setPage] = useState(0)
  const [selected, setSelected] = useState(null)
  const [children, setChildren] = useState([])
  const [dashboard, setDashboard] = useState(null)
  const [form, setForm] = useState({ user_id: '', phone: '', address: '' })
  const limit = 20

  useEffect(() => { load() }, [page])

  const load = async () => {
    setLoading(true); setError('')
    try { setItems(await listResources(auth.token, 'parents', `skip=${page * limit}&limit=${limit}`)) }
    catch (err) { setError(err.message) } finally { setLoading(false) }
  }

  const handleSubmit = async (e) => {
    e.preventDefault(); setError('')
    const toastId = toast.loading('Creating...')
    try {
      await createResource(auth.token, 'parents', { ...form, user_id: Number(form.user_id) })
      toast.success('Created!', { id: toastId })
      setForm({ user_id: '', phone: '', address: '' }); await load()
    } catch (err) { setError(err.message); toast.error(err.message, { id: toastId }) }
  }

  const handleView = async (id) => {
    setSelected(id)
    try {
      const [profile, childData, dashData] = await Promise.all([
        getResource(auth.token, 'parents', `${id}/profile`),
        listResources(auth.token, `parents/${id}/children`),
        listResources(auth.token, `parents/${id}/dashboard`),
      ])
      setChildren(Array.isArray(childData) ? childData : [])
      setDashboard(dashData)
    } catch (err) { toast.error(err.message) }
  }

  const handleDelete = async (id) => {
    if (!window.confirm('Delete this parent?')) return
    try { await deleteResource(auth.token, 'parents', id); toast.success('Deleted'); await load() }
    catch (err) { toast.error(err.message) }
  }

  return (
    <PageWrapper title="Parents">
      <div className="card" style={{ marginBottom: 24 }}>
        <h2>Create Parent</h2>
        <form onSubmit={handleSubmit} className="form-grid">
          <input className="input" type="number" value={form.user_id} onChange={(e) => setForm({ ...form, user_id: e.target.value })} placeholder="User ID" required />
          <input className="input" value={form.phone} onChange={(e) => setForm({ ...form, phone: e.target.value })} placeholder="Phone" />
          <input className="input" value={form.address} onChange={(e) => setForm({ ...form, address: e.target.value })} placeholder="Address" />
          <button className="btn btn-primary" type="submit">Create</button>
        </form>
      </div>
      <div className="card">
        <h2>Parent List</h2>
        {loading ? <div className="skeleton-list">{Array.from({ length: 5 }).map((_, i) => <div key={i} className="skeleton-row" />)}</div>
        : items.length === 0 ? <div className="empty-state">No parents found.</div>
        : <div className="table-responsive">
            <table className="data-table">
              <thead><tr><th>ID</th><th>User ID</th><th>Phone</th><th>Address</th><th>Actions</th></tr></thead>
              <tbody>
                {items.map((item) => (
                  <tr key={item.id}>
                    <td>{item.id}</td><td>{item.user_id}</td><td>{item.phone || '-'}</td><td>{item.address || '-'}</td>
                    <td className="action-cell">
                      <button className="btn btn-sm" onClick={() => handleView(item.id)}>View</button>
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

      {selected && dashboard && (
        <div className="card">
          <h2>Parent Dashboard (ID: {selected})</h2>
          <div className="metrics-grid">
            <div className="metric-card"><h3>Children</h3><p>{children.length}</p></div>
          </div>
          {dashboard.children && dashboard.children.map((child) => (
            <div key={child.student_id} className="card" style={{ marginTop: 12 }}>
              <h3>Student #{child.student_id} ({child.admission_no || 'N/A'})</h3>
              <div className="metrics-grid" style={{ marginTop: 8 }}>
                <div className="metric-card"><h3>Present</h3><p>{child.present_count}</p></div>
                <div className="metric-card"><h3>Absent</h3><p>{child.absent_count}</p></div>
                <div className="metric-card"><h3>Pending Fees</h3><p>{child.pending_fee_assignments}</p></div>
              </div>
            </div>
          ))}
        </div>
      )}
      {error && <div className="error-banner">{error}</div>}
    </PageWrapper>
  )
}
