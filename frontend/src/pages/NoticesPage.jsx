import React, { useEffect, useState } from 'react'
import PageWrapper from '../components/PageWrapper'
import { useAuth } from '../hooks/useAuth'
import { listResources, createResource } from '../api'

export default function NoticesPage() {
  const auth = useAuth()
  const [notices, setNotices] = useState([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [form, setForm] = useState({ title: '', content: '', target_roles: '' })

  useEffect(() => {
    loadNotices()
  }, [])

  const loadNotices = async () => {
    setLoading(true)
    setError('')
    try {
      const data = await listResources(auth.token, 'notices')
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
    try {
      await createResource(auth.token, 'notices', {
        title: form.title,
        content: form.content,
        target_roles: form.target_roles,
      })
      setForm({ title: '', content: '', target_roles: '' })
      await loadNotices()
    } catch (err) {
      setError(err.message)
    }
  }

  return (
    <PageWrapper title="Notices">
      <section style={{ marginBottom: 24 }}>
        <h2>Create Notice</h2>
        <form onSubmit={handleCreate} style={{ display: 'grid', gap: 12, maxWidth: 520 }}>
          <input value={form.title} onChange={(e) => setForm({ ...form, title: e.target.value })} placeholder="Title" required />
          <textarea value={form.content} onChange={(e) => setForm({ ...form, content: e.target.value })} placeholder="Content" rows={4} />
          <input value={form.target_roles} onChange={(e) => setForm({ ...form, target_roles: e.target.value })} placeholder="Target roles (comma-separated)" />
          <button type="submit" style={{ padding: '10px 16px' }}>Create</button>
        </form>
      </section>

      <section>
        <h2>Notice Board</h2>
        {loading ? (
          <p>Loading notices...</p>
        ) : (
          <div style={{ display: 'grid', gap: 12 }}>
            {notices.map((notice) => (
              <div key={notice.id} style={{ padding: 16, border: '1px solid #ddd', borderRadius: 8 }}>
                <h3>{notice.title}</h3>
                <p>{notice.content}</p>
                <p><strong>Target:</strong> {notice.target_roles || 'All'}</p>
              </div>
            ))}
          </div>
        )}
      </section>
      {error && <p style={{ color: 'red' }}>{error}</p>}
    </PageWrapper>
  )
}
