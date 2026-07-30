import React, { useEffect, useState } from 'react'
import ParentLayout from '../components/ParentLayout'
import { useAuth } from '../hooks/useAuth.jsx'
import { useParentChild } from '../components/ParentChildContext'
import { listResources, downloadFile } from '../api'

export default function ParentCertificatesPage() {
  const auth = useAuth()
  const { activeChild } = useParentChild()
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    if (activeChild) {
      loadCertificates()
    }
  }, [activeChild])

  const loadCertificates = async () => {
    if (!activeChild) return
    setLoading(true)
    try {
      const d = await listResources(auth.token, `portal/parent/children/${activeChild.student_id}/certificates`)
      setData(d)
    } catch (err) { console.error(err) }
    finally { setLoading(false) }
  }

  const handleDownload = (certId) => {
    downloadFile(auth.token, `portal/parent/children/${activeChild.student_id}/certificates/${certId}/download`, `certificate_${certId}.pdf`)
  }

  if (!activeChild) {
    return (
      <ParentLayout title="Certificates">
        <div className="empty-state">No child selected. Please add children first.</div>
      </ParentLayout>
    )
  }

  if (loading) {
    return <ParentLayout title="Certificates"><div className="skeleton-list">{Array.from({ length: 3 }).map((_, i) => <div key={i} className="skeleton-row" />)}</div></ParentLayout>
  }

  return (
    <ParentLayout title={`Certificates - ${activeChild.full_name}`}>
      <div className="card">
        <h3>🎓 Certificates</h3>
        {(data?.certificates || []).length > 0 ? (
          <div className="notice-list">
            {data.certificates.map((c) => (
              <div key={c.id} className="notice-card">
                <div className="notice-header">
                  <h3>{c.certificate_type}</h3>
                  <span className="notice-date">{new Date(c.issue_date).toLocaleDateString()}</span>
                </div>
                <div className="notice-content">
                  {c.remarks && <p>{c.remarks}</p>}
                </div>
                <div className="notice-meta">
                  <button className="btn btn-sm btn-primary" onClick={() => handleDownload(c.id)}>📥 Download PDF</button>
                </div>
              </div>
            ))}
          </div>
        ) : <div className="empty-state">No certificates available</div>}
      </div>
    </ParentLayout>
  )
}