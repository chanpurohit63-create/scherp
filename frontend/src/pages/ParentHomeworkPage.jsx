import React, { useEffect, useState } from 'react'
import { useParams } from 'react-router-dom'
import ParentLayout from '../components/ParentLayout'
import { useAuth } from '../hooks/useAuth.jsx'
import { listResources } from '../api'

export default function ParentHomeworkPage() {
  const auth = useAuth()
  const { studentId } = useParams()
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => { loadHomework() }, [studentId])

  const loadHomework = async () => {
    try {
      const d = await listResources(auth.token, `portal/parent/children/${studentId}/homework`)
      setData(d)
    } catch (err) { console.error(err) }
    finally { setLoading(false) }
  }

  if (loading) {
    return <ParentLayout title="Homework"><div className="skeleton-list">{Array.from({ length: 5 }).map((_, i) => <div key={i} className="skeleton-row" />)}</div></ParentLayout>
  }

  return (
    <ParentLayout title="Homework">
      <div className="notice-list">
        {(data?.homework || []).map(({ homework, submission, status }) => (
          <div key={homework.id} className="notice-card">
            <div className="notice-header">
              <h3>{homework.title}</h3>
              <span className="role-badge" style={{
                background: status === 'pending' ? '#fef3c7' : status === 'submitted' ? '#dbeafe' : '#d1fae5',
                color: status === 'pending' ? '#92400e' : status === 'submitted' ? '#1e40af' : '#065f46'
              }}>{status}</span>
            </div>
            <div className="notice-content">{homework.description || ''}</div>
            <div className="notice-meta">
              <span>Due: {homework.due_date ? new Date(homework.due_date).toLocaleDateString() : '-'}</span>
              {submission?.grade && <span>Grade: <strong>{submission.grade}</strong></span>}
              {submission?.feedback && <span>Feedback: {submission.feedback}</span>}
              {homework.attachment_path && <span className="notice-attachment">📎 <a href={`http://127.0.0.1:8000/${homework.attachment_path}`} target="_blank">Download</a></span>}
            </div>
          </div>
        ))}
        {(!data?.homework || data.homework.length === 0) && <div className="empty-state">No homework</div>}
      </div>
    </ParentLayout>
  )
}
