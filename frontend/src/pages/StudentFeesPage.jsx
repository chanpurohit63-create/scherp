import React, { useEffect, useState } from 'react'
import StudentLayout from '../components/StudentLayout'
import { useAuth } from '../hooks/useAuth.jsx'
import { listResources, downloadFile } from '../api'

export default function StudentFeesPage() {
  const auth = useAuth()
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => { loadFees() }, [])

  const loadFees = async () => {
    try {
      const d = await listResources(auth.token, 'portal/student/fees')
      setData(d)
    } catch (err) { console.error(err) }
    finally { setLoading(false) }
  }

  const handleReceipt = (paymentId) => {
    downloadFile(auth.token, `portal/student/fees/receipt/${paymentId}`, `receipt_${paymentId}.pdf`)
  }

  if (loading) {
    return <StudentLayout title="Fees"><div className="skeleton-list"><div className="skeleton-row" /></div></StudentLayout>
  }

  return (
    <StudentLayout title="Fees">
      <div className="card">
        <h3>Fee Structure & Pending Dues</h3>
        {(data?.pending || []).length > 0 ? (
          <div className="table-responsive">
            <table className="data-table">
              <thead>
                <tr><th>Fee Name</th><th>Amount</th><th>Due Date</th><th>Status</th></tr>
              </thead>
              <tbody>
                {data.pending.map(({ assignment, structure }) => (
                  <tr key={assignment.id}>
                    <td>{structure.name}</td>
                    <td>${structure.amount}</td>
                    <td>{assignment.due_date || '-'}</td>
                    <td><span className="role-badge" style={{ background: '#fee2e2', color: '#991b1b' }}>Pending</span></td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : <div className="empty-state">No pending fees</div>}
      </div>

      <div className="card" style={{ marginTop: 20 }}>
        <h3>Payment History</h3>
        {(data?.payments || []).length > 0 ? (
          <div className="table-responsive">
            <table className="data-table">
              <thead>
                <tr><th>Amount</th><th>Date</th><th>Reference</th><th>Receipt</th></tr>
              </thead>
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
        ) : <div className="empty-state">No payment history</div>}
      </div>
    </StudentLayout>
  )
}
