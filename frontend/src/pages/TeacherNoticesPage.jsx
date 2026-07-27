import React, { useEffect, useState } from 'react'
import TeacherLayout from '../components/TeacherLayout'
import { useAuth } from '../hooks/useAuth.jsx'
import { listResources, createResource } from '../api'
import toast from 'react-hot-toast'

export default function TeacherNoticesPage() {
  const auth = useAuth()
  const [notices, setNotices] = useState([])
  const [showForm, setShowForm] = useState(false)
  const [form, setForm] = useState({ title: '', content: '', target_roles: 'all' })
  const [loading, setLoading] = useState(true)

  useEffect(() => { loadNotices() }, [])

  const loadNotices = async () => {
    try {
      const d = await listResources(auth.token, 'notices')
      setNotices(d || [])
    } catch (err) { console.error(err) }
    finally { setLoading(false) }
  }

  const handleCreate = async () => {
    if (!form.title) { toast.error('Title required'); return }
    try {
      await createResource(auth.token, 'portal/teacher/notices', form)
      toast.success('Notice created')
      setShowForm(false)
      setForm({ title: '', content: '', target_roles: 'all' })
      loadNotices()
    } catch (err) { toast.error('Create failed') }
  }

  if (loading) {
    return <TeacherLayout title="Notices"><div className="skeleton-card" style={{ height: 200 }} /></TeacherLayout>
  }

  return (
    <TeacherLayout title="Notices">
      <div className="list-header">
        <h2>Notices</h2>
        <button className="btn btn-primary" onClick={() => setShowForm(true)}>+ New Notice</button>
      </div>

      {showForm && (
        <div className="card" style={{ marginBottom: 16 }}>
          <h3>Create Notice</h3>
          <div className="form-grid">
            <label>Title <input className="input" value={form.title} onChange={(e) => setForm({ ...form, title: e.target.value })} /></label>
            <label>Content <textarea className="input" value={form.content} onChange={(e) => setForm({ ...form, content: e.target.value })} /></label>
            <label>Target
              <select className="input" value={form.target_roles} onChange={(e) => setForm({ ...form, target_roles: e.target.value })}>
                <option value="all">All</option>
                <option value="Student">Students</option>
                <option value="Teacher">Teachers</option>
                <option value="Parent">Parents</option>
              </select>
            </label>
          </div>
          <div className="form-actions">
            <button className="btn btn-primary" onClick={handleCreate}>Publish</button>
            <button className="btn" onClick={() => setShowForm(false)}>Cancel</button>
          </div>
        </div>
      )}

      <div className="notice-list">
        {notices.length === 0 && <div className="empty-state">No notices</div>}
        {notices.map((notice) => (
          <div key={notice.id} className="notice-card">
            <div className="notice-header"><h3>{notice.title}</h3></div>
            <div className="notice-content">{notice.content}</div>
            <div className="notice-meta">
              <span className="notice-date">{new Date(notice.created_on).toLocaleDateString()}</span>
              <span className="notice-tag">{notice.target_roles || 'All'}</span>
            </div>
          </div>
        ))}
      </div>
    </TeacherLayout>
  )
}

