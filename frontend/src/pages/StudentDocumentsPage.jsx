import React, { useEffect, useState } from 'react'
import StudentLayout from '../components/StudentLayout'
import { useAuth } from '../hooks/useAuth.jsx'
import { listResources, downloadFile } from '../api'

export default function StudentDocumentsPage() {
  const auth = useAuth()
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => { loadDocuments() }, [])

  const loadDocuments = async () => {
    try {
      const d = await listResources(auth.token, 'portal/student/documents')
      setData(d)
    } catch (err) { console.error(err) }
    finally { setLoading(false) }
  }

  const handleDownload = (path, name) => {
    downloadFile(auth.token, path.replace('static/', ''), name)
  }

  if (loading) {
    return <StudentLayout title="Documents"><div className="skeleton-list"><div className="skeleton-row" /></div></StudentLayout>
  }

  return (
    <StudentLayout title="Documents">
      <div className="card">
        <h3>📄 My Documents</h3>
        {(data?.documents || []).length > 0 ? (
          <div className="table-responsive">
            <table className="data-table">
              <thead><tr><th>Name</th><th>Uploaded</th><th>Download</th></tr></thead>
              <tbody>
                {data.documents.map((d) => (
                  <tr key={d.id}>
                    <td>{d.name}</td>
                    <td>{new Date(d.uploaded_on).toLocaleDateString()}</td>
                    <td><button className="btn btn-sm" onClick={() => handleDownload(d.file_path, d.name)}>Download</button></td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : <div className="empty-state">No documents</div>}
      </div>

      <div className="card" style={{ marginTop: 20 }}>
        <h3>🎓 Certificates</h3>
        {(data?.certificates || []).length > 0 ? (
          <div className="table-responsive">
            <table className="data-table">
              <thead><tr><th>Type</th><th>Issue Date</th><th>Download</th></tr></thead>
              <tbody>
                {data.certificates.map((c) => (
                  <tr key={c.id}>
                    <td>{c.certificate_type}</td>
                    <td>{new Date(c.issue_date).toLocaleDateString()}</td>
                    <td>
                      {c.file_path ? <button className="btn btn-sm" onClick={() => handleDownload(c.file_path, `certificate_${c.id}.pdf`)}>Download</button> : '-'}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : <div className="empty-state">No certificates</div>}
      </div>

      <div className="card" style={{ marginTop: 20 }}>
        <h3>🧾 Fee Receipts</h3>
        {(data?.payments || []).length > 0 ? (
          <div className="table-responsive">
            <table className="data-table">
              <thead><tr><th>Amount</th><th>Date</th><th>Receipt</th></tr></thead>
              <tbody>
                {data.payments.map((p) => (
                  <tr key={p.id}>
                    <td>${p.amount}</td>
                    <td>{new Date(p.paid_on).toLocaleDateString()}</td>
                    <td><button className="btn btn-sm" onClick={() => downloadFile(auth.token, `portal/student/fees/receipt/${p.id}`, `receipt_${p.id}.pdf`)}>Download</button></td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : <div className="empty-state">No receipts</div>}
      </div>
    </StudentLayout>
  )
}
