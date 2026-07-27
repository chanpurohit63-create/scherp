import React, { useEffect, useState } from 'react'
import ParentLayout from '../components/ParentLayout'
import { useAuth } from '../hooks/useAuth.jsx'
import { listResources } from '../api'

export default function ParentNoticesPage() {
  const auth = useAuth()
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(true)
  const [search, setSearch] = useState('')
  const [page, setPage] = useState(0)

  useEffect(() => { loadNotices() }, [page])

  const loadNotices = async () => {
    try {
      const params = new URLSearchParams({ skip: page * 20, limit: '20' })
      if (search) params.set('search', search)
      const d = await listResources(auth.token, 'portal/parent/notices', params.toString())
      setData(d)
    } catch (err) { console.error(err) }
    finally { setLoading(false) }
  }

  if (loading) {
    return <ParentLayout title="Notices"><div className="skeleton-list">{Array.from({ length: 5 }).map((_, i) => <div key={i} className="skeleton-row" />)}</div></ParentLayout>
  }

  return (
    <ParentLayout title="Notices">
      <div className="filter-bar">
        <input className="input search-input" placeholder="Search notices..." value={search} onChange={(e) => setSearch(e.target.value)} />
        <button className="btn btn-primary btn-sm" onClick={() => { setPage(0); loadNotices() }}>Search</button>
      </div>
      <div className="notice-list">
        {(data?.notices || []).map((n) => (
          <div key={n.id} className="notice-card">
            <div className="notice-header">
              <h3>{n.title}</h3>
              <span className="notice-date">{new Date(n.created_on).toLocaleDateString()}</span>
            </div>
            <div className="notice-content">{n.content || ''}</div>
            <div className="notice-meta">
              <span className="notice-tag">{n.target_roles || 'All'}</span>
              {n.attachments_path && <span className="notice-attachment">📎 <a href={`http://127.0.0.1:8000/${n.attachments_path}`} target="_blank">Download</a></span>}
            </div>
          </div>
        ))}
        {(!data?.notices || data.notices.length === 0) && <div className="empty-state">No notices</div>}
      </div>
      <div className="pagination">
        <button className="btn btn-sm" disabled={page === 0} onClick={() => setPage(page - 1)}>Previous</button>
        <span>Page {page + 1}</span>
        <button className="btn btn-sm" onClick={() => setPage(page + 1)}>Next</button>
      </div>
    </ParentLayout>
  )
}
