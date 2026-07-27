import React, { useEffect, useState } from 'react'
import PageWrapper from '../components/PageWrapper'
import { useAuth } from '../hooks/useAuth.jsx'
import { listResources, createResource, uploadFile, deleteResource, getBackendUrl } from '../api'
import toast from 'react-hot-toast'

export default function NoticesPage() {
  const auth = useAuth()
  const [notices, setNotices] = useState([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [form, setForm] = useState({ title: '', content: '', target_roles: '', scheduled_for: '' })
  const [attachment, setAttachment] = useState(null)
  const [search, setSearch] = useState('')
  const [page, setPage] = useState(0)
  const pageSize = 10

  useEffect(() => {
    loadNotices()
  }, [page, search])

  const buildQuery = () => {
    const params = new URLSearchParams({ skip: page * pageSize, limit: pageSize })
    if (search) params.set('query', search)
    return params.toString()
  }

  const loadNotices = async () => {
    setLoading(true)
    setError('')
    try {
      const data = await listResources(auth.token, 'notices', buildQuery())
      setNotices(data)
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  const handleCreate = async (event) => {
    event.preventDefault()
    setError('')
    const toastId = toast.loading('Creating notice...')
    try {
      const roles = form.target_roles === 'all' ? 'all' : form.target_roles
      const notice = await createResource(auth.token, 'notices', {
        title: form.title,
        content: form.content,
        target_roles: roles,
        scheduled_for: form.scheduled_for || null,
      })
      if (attachment) {
        await uploadFile(auth.token, `notices/${notice.id}/attachments`, attachment)
      }
      toast.success('Notice created!', { id: toastId })
      setForm({ title: '', content: '', target_roles: '', scheduled_for: '' })
      setAttachment(null)
      await loadNotices()
    } catch (err) {
      setError(err.message)
      toast.error(err.message, { id: toastId })
    }
  }

  const handleDelete = async (id) => {
    if (!window.confirm('Delete this notice?')) return
    try {
      await deleteResource(auth.token, 'notices', id)
      toast.success('Notice deleted')
      await loadNotices()
    } catch (err) {
      toast.error(err.message)
    }
  }

  return (
    <PageWrapper title="Notices">
      <section className="card" style={{ marginBottom: 24 }}>
        <h2>Create Notice</h2>
        <form onSubmit={handleCreate} className="form-grid">
          <input className="input" value={form.title} onChange={(e) => setForm({ ...form, title: e.target.value })} placeholder="Title" required />
          <textarea className="input" value={form.content} onChange={(e) => setForm({ ...form, content: e.target.value })} placeholder="Content (HTML supported)" rows={6} />
          <div className="audience-selector">
            <label>Target Audience</label>
            <div className="radio-group">
              {['all', 'Students', 'Teachers', 'Parents'].map((role) => (
                <label key={role} className="radio-label">
                  <input type="radio" name="target_roles" value={role} checked={form.target_roles === role} onChange={(e) => setForm({ ...form, target_roles: e.target.value })} />
                  {role === 'all' ? 'Everyone' : role}
                </label>
              ))}
            </div>
          </div>
          <label>
            Schedule Date (optional)
            <input className="input" type="datetime-local" value={form.scheduled_for} onChange={(e) => setForm({ ...form, scheduled_for: e.target.value })} />
          </label>
          <label>
            Attachment
            <input className="input" type="file" onChange={(e) => setAttachment(e.target.files[0])} />
          </label>
          <button className="btn btn-primary" type="submit">Create Notice</button>
        </form>
      </section>

      <section className="card">
        <div className="list-header">
          <h2>Notice Board</h2>
          <input className="input search-input" placeholder="Search notices..." value={search} onChange={(e) => { setSearch(e.target.value); setPage(0) }} />
        </div>
        {loading ? (
          <div className="skeleton-list">{Array.from({ length: 3 }).map((_, i) => <div key={i} className="skeleton-row" />)}</div>
        ) : notices.length === 0 ? (
          <div className="empty-state">No notices yet.</div>
        ) : (
          <div className="notice-list">
            {notices.map((notice) => (
              <div key={notice.id} className="notice-card">
                <div className="notice-header">
                  <h3>{notice.title}</h3>
                  <button className="btn btn-sm btn-danger" onClick={() => handleDelete(notice.id)}>Delete</button>
                </div>
                <div className="notice-content" dangerouslySetInnerHTML={{ __html: notice.content }} />
                <div className="notice-meta">
                  <span className="notice-tag">Target: {notice.target_roles || 'All'}</span>
                  <span className="notice-date">{new Date(notice.created_on).toLocaleString()}</span>
                  {notice.scheduled_for && <span className="notice-tag">Scheduled: {new Date(notice.scheduled_for).toLocaleString()}</span>}
                  {notice.attachments_path && <a className="notice-attachment" href={`${getBackendUrl()}/static/uploads/${notice.attachments_path.split('/').pop()}`} target="_blank" rel="noopener">View Attachment</a>}
                </div>
              </div>
            ))}
          </div>
        )}
        <div className="pagination">
          <button className="btn btn-sm" disabled={page === 0} onClick={() => setPage(page - 1)}>Previous</button>
          <span>Page {page + 1}</span>
          <button className="btn btn-sm" disabled={notices.length < pageSize} onClick={() => setPage(page + 1)}>Next</button>
        </div>
      </section>
      {error && <div className="error-banner">{error}</div>}
    </PageWrapper>
  )
}
