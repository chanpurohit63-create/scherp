import React, { useEffect, useState } from 'react'
import ParentLayout from '../components/ParentLayout'
import { useAuth } from '../hooks/useAuth.jsx'
import { useParentChild } from '../components/ParentChildContext'
import { listResources, downloadFile } from '../api'

export default function ParentDocumentsPage() {
  const auth = useAuth()
  const { activeChild } = useParentChild()
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    if (activeChild) {
      loadDocuments()
    }
  }, [activeChild])

  const loadDocuments = async () => {
    if (!activeChild) return
    setLoading(true)
    try {
      const d = await listResources(auth.token, `portal/parent/children/${activeChild.student_id}/documents`)
      setData(d)
    } catch (err) { console.error(err) }
    finally { setLoading(false) }
  }

  const handleDownload = (doc) => {
    downloadFile(auth.token, `portal/student/documents/${doc.id}/download`, doc.name)
  }

  if (!activeChild) {
    return (
      <ParentLayout title="Documents">
        <div className="empty-state">No child selected. Please add children first.</div>
      </ParentLayout>
    )
  }

  if (loading) {
    return <ParentLayout title="Documents"><div className="skeleton-list">{Array.from({ length: 3 }).map((_, i) => <div key={i} className="skeleton-row" />)}</div></ParentLayout>
  }

  return (
    <ParentLayout title={`Documents - ${activeChild.full_name}`}>
      <div className="card">
        <h3>📄 Documents</h3>
        {(data?.documents || []).length > 0 ? (
          <div className="table-responsive">
            <table className="data-table">
              <thead>
                <tr><th>Name</th><th>Uploaded On</th><th>Action</th></tr>
              </thead>
              <tbody>
                {data.documents.map((d) => (
                  <tr key={d.id}>
                    <td>{d.name}</td>
                    <td>{new Date(d.uploaded_on).toLocaleDateString()}</td>
                    <td>
                      <button className="btn btn-sm" onClick={() => handleDownload(d)}>📥 Download</button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : <div className="empty-state">No documents available</div>}
      </div>
    </ParentLayout>
  )
}