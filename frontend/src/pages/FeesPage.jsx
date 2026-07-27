import React, { useEffect, useState } from 'react'
import PageWrapper from '../components/PageWrapper'
import { useAuth } from '../hooks/useAuth'
import { listResources, createResource } from '../api'

export default function FeesPage() {
  const auth = useAuth()
  const [fees, setFees] = useState([])
  const [assignments, setAssignments] = useState([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [structureForm, setStructureForm] = useState({ name: '', amount: '', category: '' })
  const [assignmentForm, setAssignmentForm] = useState({ student_id: '', fee_structure_id: '', due_date: '' })

  useEffect(() => {
    loadFeeData()
  }, [])

  const loadFeeData = async () => {
    setLoading(true)
    setError('')
    try {
      const feeData = await listResources(auth.token, 'fee-structures')
      const assignmentData = await listResources(auth.token, 'fee-assignments')
      setFees(feeData)
      setAssignments(assignmentData)
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  const handleCreateStructure = async (event) => {
    event.preventDefault()
    setError('')
    try {
      await createResource(auth.token, 'fee-structures', {
        name: structureForm.name,
        amount: Number(structureForm.amount),
        category: structureForm.category,
      })
      setStructureForm({ name: '', amount: '', category: '' })
      await loadFeeData()
    } catch (err) {
      setError(err.message)
    }
  }

  const handleCreateAssignment = async (event) => {
    event.preventDefault()
    setError('')
    try {
      await createResource(auth.token, 'fee-assignments', {
        student_id: Number(assignmentForm.student_id),
        fee_structure_id: Number(assignmentForm.fee_structure_id),
        due_date: assignmentForm.due_date || undefined,
      })
      setAssignmentForm({ student_id: '', fee_structure_id: '', due_date: '' })
      await loadFeeData()
    } catch (err) {
      setError(err.message)
    }
  }

  return (
    <PageWrapper title="Fees">
      <section style={{ marginBottom: 24 }}>
        <h2>Create Fee Structure</h2>
        <form onSubmit={handleCreateStructure} style={{ display: 'grid', gap: 12, maxWidth: 520 }}>
          <input value={structureForm.name} onChange={(e) => setStructureForm({ ...structureForm, name: e.target.value })} placeholder="Name" required />
          <input type="number" value={structureForm.amount} onChange={(e) => setStructureForm({ ...structureForm, amount: e.target.value })} placeholder="Amount" required />
          <input value={structureForm.category} onChange={(e) => setStructureForm({ ...structureForm, category: e.target.value })} placeholder="Category" />
          <button type="submit" style={{ padding: '10px 16px' }}>Create</button>
        </form>
      </section>

      <section style={{ marginBottom: 24 }}>
        <h2>Assign Fee</h2>
        <form onSubmit={handleCreateAssignment} style={{ display: 'grid', gap: 12, maxWidth: 520 }}>
          <input type="number" value={assignmentForm.student_id} onChange={(e) => setAssignmentForm({ ...assignmentForm, student_id: e.target.value })} placeholder="Student ID" required />
          <input type="number" value={assignmentForm.fee_structure_id} onChange={(e) => setAssignmentForm({ ...assignmentForm, fee_structure_id: e.target.value })} placeholder="Fee Structure ID" required />
          <input type="date" value={assignmentForm.due_date} onChange={(e) => setAssignmentForm({ ...assignmentForm, due_date: e.target.value })} />
          <button type="submit" style={{ padding: '10px 16px' }}>Assign</button>
        </form>
      </section>

      <section style={{ marginBottom: 24 }}>
        <h2>Fee Structures</h2>
        {loading ? (
          <p>Loading fee structures...</p>
        ) : (
          <table style={{ width: '100%', borderCollapse: 'collapse' }}>
            <thead>
              <tr>
                <th style={thStyle}>ID</th>
                <th style={thStyle}>Name</th>
                <th style={thStyle}>Amount</th>
                <th style={thStyle}>Category</th>
              </tr>
            </thead>
            <tbody>
              {fees.map((item) => (
                <tr key={item.id}>
                  <td style={tdStyle}>{item.id}</td>
                  <td style={tdStyle}>{item.name}</td>
                  <td style={tdStyle}>{item.amount}</td>
                  <td style={tdStyle}>{item.category}</td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </section>

      <section>
        <h2>Fee Assignments</h2>
        {loading ? (
          <p>Loading assignments...</p>
        ) : (
          <table style={{ width: '100%', borderCollapse: 'collapse' }}>
            <thead>
              <tr>
                <th style={thStyle}>ID</th>
                <th style={thStyle}>Student ID</th>
                <th style={thStyle}>Fee Structure</th>
                <th style={thStyle}>Due Date</th>
                <th style={thStyle}>Paid</th>
              </tr>
            </thead>
            <tbody>
              {assignments.map((assignment) => (
                <tr key={assignment.id}>
                  <td style={tdStyle}>{assignment.id}</td>
                  <td style={tdStyle}>{assignment.student_id}</td>
                  <td style={tdStyle}>{assignment.fee_structure_id}</td>
                  <td style={tdStyle}>{assignment.due_date}</td>
                  <td style={tdStyle}>{String(assignment.is_paid)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </section>

      {error && <p style={{ color: 'red' }}>{error}</p>}
    </PageWrapper>
  )
}

const thStyle = { borderBottom: '1px solid #ddd', padding: 8, textAlign: 'left' }
const tdStyle = { borderBottom: '1px solid #eee', padding: 8 }
