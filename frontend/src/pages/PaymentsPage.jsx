import React, { useEffect, useState } from 'react'
import PageWrapper from '../components/PageWrapper'
import { useAuth } from '../hooks/useAuth.jsx'
import { listResources, createResource, deleteResource } from '../api'
import toast from 'react-hot-toast'

export default function PaymentsPage() {
  const auth = useAuth()
  const [items, setItems] = useState([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [page, setPage] = useState(0)
  const [form, setForm] = useState({ fee_assignment_id: '', amount: '', reference: '' })
  const limit = 20

  useEffect(() => { load() }, [page])

  const load = async () => {
    setLoading(true); setError('')
    try { setItems(await listResources(auth.token, 'payments', `skip=${page * limit}&limit=${limit}`)) }
    catch (err) { setError(err.message) } finally { setLoading(false) }
  }

  const handleSubmit = async (e) => {
    e.preventDefault(); setError('')
    const toastId = toast.loading('Recording payment...')
    try {
      await createResource(auth.token, 'payments', { fee_assignment_id: Number(form.fee_assignment_id), amount: Number(form.amount), reference: form.reference || undefined })
      toast.success('Payment recorded!', { id: toastId })
      setForm({ fee_assignment_id: '', amount: '', reference: '' }); await load()
    } catch (err) { setError(err.message); toast.error(err.message, { id: toastId }) }
  }

  const handleDelete = async (id) => {
    if (!window.confirm('Delete this payment?')) return
    try { await deleteResource(auth.token, 'payments', id); toast.success('Deleted'); await load() }
    catch (err) { toast.error(err.message) }
  }

  return (
    <PageWrapper title="Payments">
      <div className="card" style={{ marginBottom: 24 }}>
        <h2>Record Payment</h2>
        <form onSubmit={handleSubmit} className="form-grid">
          <input className="input" type="number" value={form.fee_assignment_id} onChange={(e) => setForm({ ...form, fee_assignment_id: e.target.value })} placeholder="Fee Assignment ID" required />
          <input className="input" type="number" step="0.01" value={form.amount} onChange={(e) => setForm({ ...form, amount: e.target.value })} placeholder="Amount" required />
          <input className="input" value={form.reference} onChange={(e) => setForm({ ...form, reference: e.target.value })} placeholder="Reference (optional)" />
          <button className="btn btn-primary" type="submit">Record</button>
        </form>
      </div>
      <div className="card">
        <h2>Payment History</h2>
        {loading ? <div className="skeleton-list">{Array.from({ length: 5 }).map((_, i) => <div key={i} className="skeleton-row" />)}</div>
        : items.length === 0 ? <div className="empty-state">No payments found.</div>
        : <div className="table-responsive">
            <table className="data-table">
              <thead><tr><th>ID</th><th>Fee Assignment ID</th><th>Amount</th><th>Paid On</th><th>Reference</th><th>Actions</th></tr></thead>
              <tbody>
                {items.map((item) => (
                  <tr key={item.id}>
                    <td>{item.id}</td><td>{item.fee_assignment_id}</td><td>{item.amount}</td>
                    <td>{new Date(item.paid_on).toLocaleDateString()}</td><td>{item.reference || '-'}</td>
                    <td className="action-cell"><button className="btn btn-sm btn-danger" onClick={() => handleDelete(item.id)}>Delete</button></td>
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
