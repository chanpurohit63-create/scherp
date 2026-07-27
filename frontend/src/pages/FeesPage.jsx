import React, { useEffect, useState } from 'react'
import PageWrapper from '../components/PageWrapper'
import { useAuth } from '../hooks/useAuth.jsx'
import { listResources, createResource } from '../api'
import toast from 'react-hot-toast'

export default function FeesPage() {
  const auth = useAuth()
  const [fees, setFees] = useState([])
  const [assignments, setAssignments] = useState([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [structureForm, setStructureForm] = useState({ name: '', amount: '', category: '' })
  const [assignmentForm, setAssignmentForm] = useState({ student_id: '', fee_structure_id: '', due_date: '' })
  const [page, setPage] = useState(0)
  const pageSize = 10

  useEffect(() => { loadFeeData() }, [page])

  const loadFeeData = async () => {
    setLoading(true); setError('')
    try {
      const [feeData, assignmentData] = await Promise.all([
        listResources(auth.token, 'fee-structures'),
        listResources(auth.token, 'fee-assignments', `skip=${page * pageSize}&limit=${pageSize}`),
      ])
      setFees(feeData); setAssignments(assignmentData)
    } catch (err) { setError(err.message) }
    finally { setLoading(false) }
  }

  const handleCreateStructure = async (event) => {
    event.preventDefault(); setError('')
    const toastId = toast.loading('Creating fee structure...')
    try {
      await createResource(auth.token, 'fee-structures', { name: structureForm.name, amount: Number(structureForm.amount), category: structureForm.category })
      toast.success('Fee structure created!', { id: toastId })
      setStructureForm({ name: '', amount: '', category: '' })
      await loadFeeData()
    } catch (err) { setError(err.message); toast.error(err.message, { id: toastId }) }
  }

  const handleCreateAssignment = async (event) => {
    event.preventDefault(); setError('')
    const toastId = toast.loading('Assigning fee...')
    try {
      await createResource(auth.token, 'fee-assignments', { student_id: Number(assignmentForm.student_id), fee_structure_id: Number(assignmentForm.fee_structure_id), due_date: assignmentForm.due_date || undefined })
      toast.success('Fee assigned!', { id: toastId })
      setAssignmentForm({ student_id: '', fee_structure_id: '', due_date: '' })
      await loadFeeData()
    } catch (err) { setError(err.message); toast.error(err.message, { id: toastId }) }
  }

  return (
    <PageWrapper title="Fees">
      <div className="card" style={{ marginBottom: 24 }}>
        <h2>Create Fee Structure</h2>
        <form onSubmit={handleCreateStructure} className="form-grid">
          <input className="input" value={structureForm.name} onChange={(e) => setStructureForm({ ...structureForm, name: e.target.value })} placeholder="Name" required />
          <input className="input" type="number" value={structureForm.amount} onChange={(e) => setStructureForm({ ...structureForm, amount: e.target.value })} placeholder="Amount" required />
          <input className="input" value={structureForm.category} onChange={(e) => setStructureForm({ ...structureForm, category: e.target.value })} placeholder="Category" />
          <button className="btn btn-primary" type="submit">Create</button>
        </form>
      </div>
      <div className="card" style={{ marginBottom: 24 }}>
        <h2>Assign Fee</h2>
        <form onSubmit={handleCreateAssignment} className="form-grid">
          <input className="input" type="number" value={assignmentForm.student_id} onChange={(e) => setAssignmentForm({ ...assignmentForm, student_id: e.target.value })} placeholder="Student ID" required />
          <input className="input" type="number" value={assignmentForm.fee_structure_id} onChange={(e) => setAssignmentForm({ ...assignmentForm, fee_structure_id: e.target.value })} placeholder="Fee Structure ID" required />
          <input className="input" type="date" value={assignmentForm.due_date} onChange={(e) => setAssignmentForm({ ...assignmentForm, due_date: e.target.value })} />
          <button className="btn btn-primary" type="submit">Assign</button>
        </form>
      </div>
      <div className="card" style={{ marginBottom: 24 }}>
        <h2>Fee Structures</h2>
        {loading ? (
          <div className="skeleton-list">{Array.from({ length: 3 }).map((_, i) => <div key={i} className="skeleton-row" />)}</div>
        ) : (
          <div className="table-responsive">
            <table className="data-table">
              <thead><tr><th>ID</th><th>Name</th><th>Amount</th><th>Category</th></tr></thead>
              <tbody>
                {fees.map((item) => (
                  <tr key={item.id}><td>{item.id}</td><td>{item.name}</td><td>${item.amount}</td><td>{item.category}</td></tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
      <div className="card">
        <h2>Fee Assignments</h2>
        {loading ? (
          <div className="skeleton-list">{Array.from({ length: 3 }).map((_, i) => <div key={i} className="skeleton-row" />)}</div>
        ) : assignments.length === 0 ? (
          <div className="empty-state">No assignments yet.</div>
        ) : (
          <div className="table-responsive">
            <table className="data-table">
              <thead><tr><th>ID</th><th>Student ID</th><th>Fee Structure</th><th>Due Date</th><th>Paid</th></tr></thead>
              <tbody>
                {assignments.map((a) => (
                  <tr key={a.id}><td>{a.id}</td><td>{a.student_id}</td><td>{a.fee_structure_id}</td><td>{a.due_date}</td><td><span className="role-badge">{String(a.is_paid)}</span></td></tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
        <div className="pagination">
          <button className="btn btn-sm" disabled={page === 0} onClick={() => setPage(page - 1)}>Previous</button>
          <span>Page {page + 1}</span>
          <button className="btn btn-sm" disabled={assignments.length < pageSize} onClick={() => setPage(page + 1)}>Next</button>
        </div>
      </div>
      {error && <div className="error-banner">{error}</div>}
    </PageWrapper>
  )
}
