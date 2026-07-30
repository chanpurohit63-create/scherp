import React, { useEffect, useState } from 'react'
import PageWrapper from '../components/PageWrapper'
import { useAuth } from '../hooks/useAuth.jsx'
import { listResources, getBackendUrl } from '../api'

export default function ConflictMonitorPage() {
  const auth = useAuth()
  const [conflicts, setConflicts] = useState([])
  const [loading, setLoading] = useState(true)
  const [resolved, setResolved] = useState(false)

  useEffect(() => {
    loadConflicts()
  }, [])

  const loadConflicts = async () => {
    try {
      const params = new URLSearchParams()
      if (resolved) params.set('resolved', 'true')
      const data = await listResources(auth.token, `timetable/conflicts?${params.toString()}`)
      setConflicts(data)
    } catch (err) {
      console.error(err)
    } finally {
      setLoading(false)
    }
  }

  const handleResolve = async (conflictId) => {
    try {
      const response = await fetch(`${getBackendUrl()}/api/timetable/conflicts/${conflictId}/resolve`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${auth.token}` },
      })
      if (response.ok) {
        loadConflicts()
      }
    } catch (err) {
      console.error(err)
    }
  }

  if (loading) {
    return (
      <PageWrapper title="Conflict Monitor">
        <div className="skeleton-grid">
          {Array.from({ length: 4 }).map((_, i) => <div key={i} className="skeleton-card" />)}
        </div>
      </PageWrapper>
    )
  }

  return (
    <PageWrapper title="Conflict Monitor">
      <div className="flex gap-4 mb-6">
        <button
          className={`btn ${!resolved ? 'btn-primary' : 'btn-secondary'}`}
          onClick={() => { setResolved(false); setConflicts([]); loadConflicts(); }}
        >
          Unresolved
        </button>
        <button
          className={`btn ${resolved ? 'btn-primary' : 'btn-secondary'}`}
          onClick={() => { setResolved(true); setConflicts([]); loadConflicts(); }}
        >
          Resolved
        </button>
      </div>

      <div className="card">
        <h3 className="card-title">Conflicts ({conflicts.length})</h3>
        {conflicts.length === 0 ? (
          <p className="text-muted">No conflicts found.</p>
        ) : (
          <div className="table-responsive">
            <table className="table">
              <thead>
                <tr>
                  <th>Type</th>
                  <th>Description</th>
                  <th>Day</th>
                  <th>Period</th>
                  <th>Time</th>
                  <th>Teacher</th>
                  <th>Class</th>
                  <th>Room</th>
                  <th>Status</th>
                  <th>Action</th>
                </tr>
              </thead>
              <tbody>
                {conflicts.map((c) => (
                  <tr key={c.id}>
                    <td><span className="badge badge-warning">{c.conflict_type}</span></td>
                    <td>{c.conflict_description}</td>
                    <td>{c.day_of_week}</td>
                    <td>{c.period_number}</td>
                    <td>{c.start_time || '-'} - {c.end_time || '-'}</td>
                    <td>{c.teacher_id || '-'}</td>
                    <td>{c.class_id || '-'}</td>
                    <td>{c.room_id || '-'}</td>
                    <td>
                      <span className={`badge ${c.resolved ? 'badge-success' : 'badge-danger'}`}>
                        {c.resolved ? 'Resolved' : 'Unresolved'}
                      </span>
                    </td>
                    <td>
                      {!c.resolved && (
                        <button onClick={() => handleResolve(c.id)} className="btn btn-sm btn-success">Resolve</button>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </PageWrapper>
  )
}