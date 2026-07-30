import React, { useEffect, useState } from 'react'
import ParentLayout from '../components/ParentLayout'
import { useAuth } from '../hooks/useAuth.jsx'
import { useParentChild } from '../components/ParentChildContext'
import { listResources, downloadFile } from '../api'

export default function ParentPaymentHistoryPage() {
  const auth = useAuth()
  const { activeChild } = useParentChild()
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    if (activeChild) {
      loadPaymentHistory()
    }
  }, [activeChild])

  const loadPaymentHistory = async () => {
    if (!activeChild) return
    setLoading(true)
    try {
      const d = await listResources(auth.token, `portal/parent/children/${activeChild.student_id}/fees`)
      setData(d)
    } catch (err) { console.error(err) }
    finally { setLoading(false) }
  }

  const handleReceipt = (paymentId) => {
    downloadFile(auth.token, `portal/student/fees/receipt/${paymentId}`, `receipt_${paymentId}.pdf`)
  }

  if (!activeChild) {
    return (
      <ParentLayout title="Payment History">
        <div className="empty-state">No child selected. Please add children first.</div>
      </ParentLayout>
    )
  }

  if (loading) {
    return <ParentLayout title="Payment History"><div className="skeleton-list"><div className="skeleton-row" /></div></ParentLayout>
  }

  const totalPaid = (data?.payments || []).reduce((s, p) => s + p.amount, 0)

  return (
    <ParentLayout title={`Payment History - ${activeChild.full_name}`}>
      <div className="metrics-grid">
        <div className="metric-card" style={{ borderTop: '3px solid #10b981' }}>
          <span className="metric-label">Total Paid</span>
          <span className="metric-value">${totalPaid.toFixed(2)}</span>
        </div>
        <div className="metric-card" style={{ borderTop: '3px solid #ef4444' }}>
          <span className="metric-label">Total Due</span>
          <span className="metric-value">${(data?.total_due || 0).toFixed(2)}</span>
        </div>
        <div className="metric-card" style={{ borderTop: '3px solid #4f46e5' }}>
          <span className="metric-label">Payments</span>
          <span className="metric-value">{(data?.payments || []).length}</span>
        </div>
      </div>

      <div className="card">
        <h3>🧾 Payment History</h3>
        {(data?.payments || []).length > 0 ? (
          <div className="table-responsive">
            <table className="data-table">
              <thead>
                <tr><th>Amount</th><th>Date</th><th>Reference</th><th>Receipt</th></tr>
              </thead>
              <tbody>
                {data.payments.map((p) => (
                  <tr key={p.id}>
                    <td><strong>${p.amount.toFixed(2)}</strong></td>
                    <td>{new Date(p.paid_on).toLocaleDateString()}</td>
                    <td>{p.reference || '-'}</td>
                    <td>
                      <button className="btn btn-sm" onClick={() => handleReceipt(p.id)}>📥 Receipt</button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : <div className="empty-state">No payment history available</div>}
      </div>
    </ParentLayout>
  )
}