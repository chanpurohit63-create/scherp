import React, { useEffect, useState } from 'react'
import { Link, useParams } from 'react-router-dom'
import ParentLayout from '../components/ParentLayout'
import { useAuth } from '../hooks/useAuth.jsx'
import { listResources } from '../api'

export default function ParentChildrenPage() {
  const auth = useAuth()
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => { loadChildren() }, [])

  const loadChildren = async () => {
    try {
      const d = await listResources(auth.token, 'portal/parent/children')
      setData(d)
    } catch (err) { console.error(err) }
    finally { setLoading(false) }
  }

  if (loading) {
    return <ParentLayout title="Children"><div className="skeleton-list"><div className="skeleton-row" /></div></ParentLayout>
  }

  return (
    <ParentLayout title="My Children">
      {(data?.children || []).length > 0 ? (
        <div className="notice-list">
          {data.children.map((c) => (
            <div key={c.student_id} className="notice-card">
              <div style={{ display: 'flex', alignItems: 'center', gap: 16 }}>
                {c.photo_path ? <img src={`http://127.0.0.1:8000/${c.photo_path}`} alt="" style={{ width: 50, height: 50, borderRadius: '50%', objectFit: 'cover' }} />
                  : <div style={{ width: 50, height: 50, borderRadius: '50%', background: '#e2e8f0', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>👤</div>}
                <div>
                  <h3>{c.full_name}</h3>
                  <p style={{ color: '#64748b', fontSize: '0.85rem' }}>Admission: {c.admission_no} | Class: {c.class_name} | Section: {c.section_name}</p>
                </div>
              </div>
              <div className="action-cell" style={{ marginTop: 12 }}>
                <Link to={`/parent/children/${c.student_id}/attendance`} className="btn btn-sm">Attendance</Link>
                <Link to={`/parent/children/${c.student_id}/homework`} className="btn btn-sm">Homework</Link>
                <Link to={`/parent/children/${c.student_id}/exams`} className="btn btn-sm">Results</Link>
                <Link to={`/parent/children/${c.student_id}/fees`} className="btn btn-sm">Fees</Link>
                <Link to={`/parent/children/${c.student_id}/progress`} className="btn btn-sm">Progress</Link>
              </div>
            </div>
          ))}
        </div>
      ) : <div className="empty-state">No children registered</div>}
    </ParentLayout>
  )
}
