import React, { useEffect, useState } from 'react'
import PageWrapper from '../components/PageWrapper'
import { useAuth } from '../hooks/useAuth.jsx'
import { listResources, createResource, uploadFile, getBackendUrl, deleteResource } from '../api'
import toast from 'react-hot-toast'

export default function CertificatesPage() {
  const auth = useAuth()
  const [certificates, setCertificates] = useState([])
  const [students, setStudents] = useState([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [form, setForm] = useState({ student_id: '', certificate_type: 'Bonafide Certificate', remarks: '' })

  useEffect(() => {
    loadCertificates()
    loadStudents()
  }, [])

  const loadCertificates = async () => {
    setLoading(true)
    try {
      const data = await listResources(auth.token, 'certificates')
      setCertificates(data)
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  const loadStudents = async () => {
    try {
      const data = await listResources(auth.token, 'students')
      setStudents(data)
    } catch (err) {
      // silent
    }
  }

  const handleGenerate = async (e) => {
    e.preventDefault()
    setError('')
    const toastId = toast.loading('Generating certificate...')
    try {
      const cert = await createResource(auth.token, `certificates/generate?certificate_type=${encodeURIComponent(form.certificate_type)}&student_id=${form.student_id}&remarks=${encodeURIComponent(form.remarks || '')}`, {})
      toast.success('Certificate generated!', { id: toastId })
      setForm({ student_id: '', certificate_type: 'Bonafide Certificate', remarks: '' })
      await loadCertificates()
      return cert
    } catch (err) {
      setError(err.message)
      toast.error(err.message, { id: toastId })
    }
  }

  const handleDownload = async (certId) => {
    try {
      const response = await fetch(`${getBackendUrl()}/api/certificates/${certId}/download`, {
        headers: { Authorization: `Bearer ${auth.token}` },
      })
      if (!response.ok) throw new Error('Download failed')
      const blob = await response.blob()
      const url = URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `certificate_${certId}.pdf`
      a.click()
      URL.revokeObjectURL(url)
    } catch (err) {
      toast.error(err.message)
    }
  }

  const handlePreview = async (certId) => {
    window.open(`${getBackendUrl()}/api/certificates/${certId}/preview?token=${auth.token}`, '_blank')
  }

  const handleDelete = async (id) => {
    if (!window.confirm('Delete this certificate?')) return
    try {
      await deleteResource(auth.token, 'certificates', id)
      toast.success('Certificate deleted')
      await loadCertificates()
    } catch (err) {
      toast.error(err.message)
    }
  }

  return (
    <PageWrapper title="Certificates">
      <section className="card" style={{ marginBottom: 24 }}>
        <h2>Generate Certificate</h2>
        <form onSubmit={handleGenerate} className="form-grid">
          <select value={form.certificate_type} onChange={(e) => setForm({ ...form, certificate_type: e.target.value })} required>
            <option value="Bonafide Certificate">Bonafide Certificate</option>
            <option value="Transfer Certificate">Transfer Certificate</option>
            <option value="Character Certificate">Character Certificate</option>
          </select>
          <select value={form.student_id} onChange={(e) => setForm({ ...form, student_id: e.target.value })} required>
            <option value="">Select Student</option>
            {students.map((s) => (
              <option key={s.id} value={s.id}>#{s.id} - {s.admission_no || 'N/A'}</option>
            ))}
          </select>
          <textarea value={form.remarks} onChange={(e) => setForm({ ...form, remarks: e.target.value })} placeholder="Remarks (optional)" rows={2} />
          <button type="submit" className="btn btn-primary">Generate PDF</button>
        </form>
      </section>

      <section className="card">
        <h2>Certificate History</h2>
        {loading ? (
          <div className="skeleton-list">{Array.from({ length: 3 }).map((_, i) => <div key={i} className="skeleton-row" />)}</div>
        ) : certificates.length === 0 ? (
          <div className="empty-state">No certificates generated yet.</div>
        ) : (
          <div className="table-responsive">
            <table className="data-table">
              <thead>
                <tr>
                  <th>ID</th>
                  <th>Type</th>
                  <th>Student ID</th>
                  <th>Issue Date</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                {certificates.map((cert) => (
                  <tr key={cert.id}>
                    <td>{cert.id}</td>
                    <td>{cert.certificate_type}</td>
                    <td>{cert.student_id}</td>
                    <td>{new Date(cert.issue_date).toLocaleDateString()}</td>
                    <td className="action-cell">
                      <button className="btn btn-sm" onClick={() => handlePreview(cert.id)}>Preview</button>
                      <button className="btn btn-sm btn-primary" onClick={() => handleDownload(cert.id)}>Download</button>
                      <button className="btn btn-sm btn-danger" onClick={() => handleDelete(cert.id)}>Delete</button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </section>
      {error && <div className="error-banner">{error}</div>}
    </PageWrapper>
  )
}

