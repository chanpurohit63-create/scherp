import React, { useEffect, useState } from 'react'
import TeacherLayout from '../components/TeacherLayout'
import { useAuth } from '../hooks/useAuth.jsx'
import { listResources, createResource } from '../api'
import toast from 'react-hot-toast'

export default function TeacherMessagesPage() {
  const auth = useAuth()
  const [messages, setMessages] = useState([])
  const [unread, setUnread] = useState(0)
  const [showForm, setShowForm] = useState(false)
  const [form, setForm] = useState({ subject: '', body: '', recipient_id: '' })
  const [search, setSearch] = useState('')
  const [loading, setLoading] = useState(true)

  useEffect(() => { loadMessages() }, [])

  const loadMessages = async () => {
    try {
      const d = await listResources(auth.token, `portal/teacher/messages${search ? `?search=${search}` : ''}`)
      setMessages(d.messages || [])
      setUnread(d.unread || 0)
    } catch (err) { console.error(err) }
    finally { setLoading(false) }
  }

  const handleSend = async () => {
    if (!form.subject || !form.recipient_id) { toast.error('Subject and recipient required'); return }
    try {
      await createResource(auth.token, 'portal/teacher/messages', {
        subject: form.subject, body: form.body,
        recipient_id: parseInt(form.recipient_id), sender_id: 0,
      })
      toast.success('Message sent')
      setShowForm(false)
      setForm({ subject: '', body: '', recipient_id: '' })
      loadMessages()
    } catch (err) { toast.error('Send failed') }
  }

  useEffect(() => { loadMessages() }, [search])

  if (loading) {
    return <TeacherLayout title="Messages"><div className="skeleton-card" style={{ height: 200 }} /></TeacherLayout>
  }

  return (
    <TeacherLayout title={`Messages (${unread} unread)`}>
      <div className="list-header">
        <input className="input search-input" placeholder="Search..." value={search} onChange={(e) => setSearch(e.target.value)} />
        <button className="btn btn-primary" onClick={() => setShowForm(true)}>+ New Message</button>
      </div>

      {showForm && (
        <div className="card" style={{ marginBottom: 16 }}>
          <h3>Send Message</h3>
          <div className="form-grid">
            <label>Recipient ID <input className="input" type="number" value={form.recipient_id} onChange={(e) => setForm({ ...form, recipient_id: e.target.value })} /></label>
            <label>Subject <input className="input" value={form.subject} onChange={(e) => setForm({ ...form, subject: e.target.value })} /></label>
            <label>Body <textarea className="input" value={form.body} onChange={(e) => setForm({ ...form, body: e.target.value })} /></label>
          </div>
          <div className="form-actions">
            <button className="btn btn-primary" onClick={handleSend}>Send</button>
            <button className="btn" onClick={() => setShowForm(false)}>Cancel</button>
          </div>
        </div>
      )}

      <div className="card">
        <h3>Conversations</h3>
        {messages.length === 0 && <div className="empty-state">No messages</div>}
        <div className="notice-list">
          {messages.map((msg) => (
            <div key={msg.id} className={`notice-card ${!msg.is_read ? 'notice-card--unread' : ''}`}>
              <div className="notice-header">
                <h3>{msg.subject}</h3>
                <span className={msg.is_read ? 'notice-tag' : 'role-badge'}>{msg.is_read ? 'Read' : 'New'}</span>
              </div>
              <div className="notice-content">{msg.body}</div>
              <div className="notice-meta">
                <span>{new Date(msg.sent_on).toLocaleString()}</span>
                <span>{msg.sender_id === auth.profile?.id ? 'Sent' : 'Received'}</span>
              </div>
            </div>
          ))}
        </div>
      </div>
    </TeacherLayout>
  )
}

