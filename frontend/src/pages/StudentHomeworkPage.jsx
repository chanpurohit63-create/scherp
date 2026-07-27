import React, { useEffect, useState } from 'react'
import StudentLayout from '../components/StudentLayout'
import { useAuth } from '../hooks/useAuth.jsx'
import { listResources, uploadFile } from '../api'
import toast from 'react-hot-toast'

export default function StudentHomeworkPage() {
  const auth = useAuth()
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(true)
  const [search, setSearch] = useState('')
  const [statusFilter, setStatusFilter] = useState('')
  const [submitting, setSubmitting] = useState(null)

  useEffect(() => { loadHomework() }, [])

  const loadHomework = async () => {
    try {
      const params = new URLSearchParams()
      if (statusFilter) params.set('status_filter', statusFilter)
      const d = await listResources(auth.token, 'portal/student/homework', params.toString())
      setData(d)
    } catch (err) { console.error(err) }
    finally { setLoading(false) }
  }

  const handleSubmit = async (homeworkId, file) => {
    if (!file) { toast.error('Select a file'); return }
    setSubmitting(homeworkId)
    try {
      await uploadFile(auth.token, `portal/student/homework/${homeworkId}/submit`, file)
      toast.success('Submitted successfully')
      loadHomework()
    } catch (err) {
      toast.error('Submission failed')
    }
    setSubmitting(null)
  }

  const getStatusBadge = (status) => {
    const colors = { pending: '#f59e0b', submitted: '#4f46e5', graded: '#10b981', late: '#ef4444' }
    return <span className="role-badge" style={{ background: `${colors[status] || '#94a3b8'}20`, color: colors[status] || '#475569' }}>{status}</span>
  }

  if (loading) {
    return <StudentLayout title="Homework"><div className="skeleton-list">{Array.from({ length: 5 }).map((_, i) => <div key={i} className="skeleton-row" />)}</div></StudentLayout>
  }

  const filtered = (data?.homework || []).filter((h) =>
    !search || h.homework.title.toLowerCase().includes(search.toLowerCase())
  )

  return (
    <StudentLayout title="Homework">
      <div className="filter-bar">
        <input className="input search-input" placeholder="Search homework..." value={search} onChange={(e) => setSearch(e.target.value)} />
        <select className="input" style={{ maxWidth: 150 }} value={statusFilter} onChange={(e) => { setStatusFilter(e.target.value); loadHomework() }}>
          <option value="">All Status</option>
          <option value="pending">Pending</option>
          <option value="submitted">Submitted</option>
          <option value="graded">Graded</option>
          <option value="late">Late</option>
        </select>
      </div>

      <div className="notice-list">
        {filtered.map(({ homework, submission, status }) => (
          <div key={homework.id} className="notice-card">
            <div className="notice-header">
              <h3>{homework.title}</h3>
              {getStatusBadge(status)}
            </div>
            <div className="notice-content">{homework.description || 'No description'}</div>
            <div className="notice-meta">
              <span>Due: {homework.due_date ? new Date(homework.due_date).toLocaleDateString() : 'No date'}</span>
              {homework.attachment_path && <span className="notice-attachment">📎 <a href={`http://127.0.0.1:8000/${homework.attachment_path}`} target="_blank">Download</a></span>}
              {submission?.grade && <span>Grade: <strong>{submission.grade}</strong></span>}
              {submission?.feedback && <span>Feedback: {submission.feedback}</span>}
            </div>
            {status === 'pending' || status === 'late' ? (
              <div style={{ marginTop: 12 }}>
                <input type="file" id={`file-${homework.id}`} style={{ display: 'none' }}
                  onChange={(e) => e.target.files[0] && handleSubmit(homework.id, e.target.files[0])} />
                <button className="btn btn-sm btn-primary" disabled={submitting === homework.id}
                  onClick={() => document.getElementById(`file-${homework.id}`).click()}>
                  {submitting === homework.id ? 'Uploading...' : 'Submit Homework'}
                </button>
              </div>
            ) : submission?.attachment_path && (
              <div style={{ marginTop: 8 }}>
                <span className="notice-attachment">📎 <a href={`http://127.0.0.1:8000/${submission.attachment_path}`} target="_blank">View Submission</a></span>
              </div>
            )}
          </div>
        ))}
        {filtered.length === 0 && <div className="empty-state">No homework found</div>}
      </div>
    </StudentLayout>
  )
}
