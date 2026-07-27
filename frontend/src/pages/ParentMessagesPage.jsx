import React, { useEffect, useState } from 'react'
import ParentLayout from '../components/ParentLayout'
import { useAuth } from '../hooks/useAuth.jsx'
import { listResources, createResource } from '../api'
import toast from 'react-hot-toast'

export default function ParentMessagesPage() {
  const auth = useAuth()
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(true)
  const [showCompose, setShowCompose] = useState(false)
  const [subject, setSubject] = useState('')
  const [body, setBody] = useState('')
  const [recipientId, setRecipientId] = useState('')

  useEffect(() => { loadMessages() }, [])

  const loadMessages = async () => {
    try {
      const d = await listResources(auth.token, 'portal/parent/messages')
      setData(d)
    } catch (err) { console.error(err) }
    finally { setLoading(false) }
  }

  const handleSend = async () => {
    if (!subject || !recipientId) { toast.error('Fill subject and recipient'); return }
    try {
      await createResource(auth.token, 'portal/parent/messages', { subject, body, recipient_id: parseInt(recipientId), sender_id: auth.profile.id })
      toast.success('Message sent')
      setShowCompose(false)
      setSubject('')
      setBody('')
      setRecipientId('')
      loadMessages()
    } catch (err) { toast.error('Failed to send') }
  }

  if (loading) {
    return <ParentLayout title="Messages"><div className="skeleton-list"><div className="skeleton-row" /></div></ParentLayout>
  }

  return (
    <ParentLayout title="Messages">
      <div className="list-header">
        <h3>Inbox ({data?.unread || 0} unread)</h3>
        <button className="btn btn-primary btn-sm" onClick={() => setShowCompose(!showCompose)}>{showCompose ? 'Cancel' : 'Compose'}</button>
      </div>
      {showCompose && (
        <div className="card" style={{ marginBottom: 20 }}>
          <h3>New Message</h3>
          <div className="form-grid">
            <label>Recipient ID <input className="input" type="number" value={recipientId} onChange={(e) => setRecipientId(e.target.value)} placeholder="Teacher/Admin user ID" /></label>
            <label>Subject <input className="input" value={subject} onChange={(e) => setSubject(e.target.value)} /></label>
            <label>Message <textarea className="input" value={body} onChange={(e) => setBody(e.target.value)} /></label>
          </div>
          <button className="btn btn-primary" onClick={handleSend}>Send</button>
        </div>
      )}
      <div className="notice-list">
        {(data?.messages || []).map((m) => (
          <div key={m.id} className="notice-card">
            <div className="notice-header">
              <h3>{m.subject}</h3>
              <span className="notice-date">{new Date(m.sent_on).toLocaleDateString()}</span>
            </div>
            <div className="notice-content">{m.body || ''}</div>
            <div className="notice-meta">
              <span>From: User #{m.sender_id}</span>
              <span>To: User #{m.recipient_id}</span>
              {!m.is_read && <span className="role-badge" style={{ background: '#4f46e5', color: '#fff' }}>New</span>}
            </div>
          </div>
        ))}
        {(!data?.messages || data.messages.length === 0) && <div className="empty-state">No messages</div>}
      </div>
    </ParentLayout>
  )
}
