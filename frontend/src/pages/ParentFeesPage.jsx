import React, { useEffect, useState } from 'react'
import { useParams } from 'react-router-dom'
import ParentLayout from '../components/ParentLayout'
import { useAuth } from '../hooks/useAuth.jsx'
import { listResources, downloadFile } from '../api'

export default function ParentFeesPage() {
  const auth = useAuth()
  const { studentId } = useParams()
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => { loadFees() }, [studentId])

  const loadFees = async () => {
    try {
      const d = await listResources(auth.token, `portal/parent/children/${studentId}/fees`)
      setData(d)
    } catch (err) { console.error(err) }
    finally { setLoading(false) }
  }

  const handleReceipt = (paymentId) => {
    downloadFile(auth.token, `portal/student/fees/receipt/${paymentId}`, `receipt_${paymentId}.pdf`)
  }

  if (loading) {
    return <ParentLayout title="Fees"><div className="skeleton-list"><div className="skeleton-row" /></div></ParentLayout>
  }

  return (
    <ParentLayout title="Fees">
      <div className="metrics-grid">
        <div className="metric-card" style={{ borderTop: '3px solid #ef4444' }}>
          <span className="metric-label">Total Due</span>
          <span className="metric-value">${data?.total_due || 0}</span>
        </div>
        <div className="metric-card" style={{ borderTop: '3px solid #10b981' }}>
          <span className="metric-label">Total Paid</span>
          <span className="metric-value">${data?.payments?.reduce((s, p) => s + p.amount, 0) || 0}</span>
        </div>
      </div>

      <div className="card">
        <h3>Fee Assignments</h3>
        {(data?.assignments || []).length > 0 ? (
          <div className="table-responsive">
            <table className="data-table">
              <thead><tr><th>Fee</th><th>Amount</th><th>Due Date</th><th>Status</th></tr></thead>
              <tbody>
                {data.assignments.map(({ assignment, structure }) => (
                  <tr key={assignment.id}>
                    <td>{structure.name}</td>
                    <td>${structure.amount}</td>
                    <td>{assignment.due_date || '-'}</td>
                    <td>{assignment.is_paid ? <span className="role-badge" style={{ background: '#d1fae5', color: '#065f46' }}>Paid</span> : <span className="role-badge" style={{ background: '#fee2e2', color: '#991b1b' }}>Pending</span>}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : <div className="empty-state">No fee assignments</div>}
      </div>

      <div className="card" style={{ marginTop: 20 }}>
        <h3>Payment History</h3>
        {(data?.payments || []).length > 0 ? (
          <div className="table-responsive">
            <table className="data-table">
              <thead><tr><th>Amount</th><th>Date</th><th>Reference</th><th>Receipt</th></tr></thead>
              <tbody>
                {data.payments.map((p) => (
                  <tr key={p.id}>
                    <td>${p.amount}</td>
                    <td>{new Date(p.paid_on).toLocaleDateString()}</td>
                    <td>{p.reference || '-'}</td>
                    <td><button className="btn btn-sm" onClick={() => handleReceipt(p.id)}>Download</button></td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : <div className="empty-state">No payments</div>}
      </div>
    </ParentLayout>
  )
}
