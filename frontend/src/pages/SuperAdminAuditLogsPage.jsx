import React, { useEffect, useState } from 'react'
import SuperAdminLayout from '../components/SuperAdminLayout'
import { useAuth } from '../hooks/useAuth.jsx'
import { listResources } from '../api'
import toast from 'react-hot-toast'

export default function SuperAdminAuditLogsPage() {
  const auth = useAuth()
  const [logs, setLogs] = useState([])
  const [loading, setLoading] = useState(true)
  const [actionFilter, setActionFilter] = useState('')

  useEffect(() => { loadLogs() }, [actionFilter])

  const loadLogs = async () => {
    try {
      const params = new URLSearchParams()
      if (actionFilter) params.append('action', actionFilter)
      params.append('skip', '0')
      params.append('limit', '100')
      const data = await listResources(auth.token, 'superadmin/audit-logs', params.toString())
      setLogs(data)
    } catch (err) {
      console.error(err)
      toast.error('Failed to load audit logs')
    } finally {
      setLoading(false)
    }
  }

  const getActionColor = (action) => {
    if (action.includes('created')) return 'badge badge-success'
    if (action.includes('updated') || action.includes('changed')) return 'badge badge-primary'
    if (action.includes('deleted') || action.includes('suspended')) return 'badge badge-danger'
    if (action.includes('activated')) return 'badge badge-success'
    return 'badge badge-gray'
  }

  if (loading) {
    return (
      <SuperAdminLayout title="Audit Logs" breadcrumbs={[{ label: 'Audit Logs', to: null }]}>
        <div className="skeleton-list">
          {Array.from({ length: 10 }).map((_, i) => <div key={i} className="skeleton-row" />)}
        </div>
      </SuperAdminLayout>
    )
  }

  return (
    <SuperAdminLayout title="Audit Logs" breadcrumbs={[{ label: 'Audit Logs', to: null }]}>
      <div className="table-container">
        <div className="table-header">
          <h3>System Audit Logs</h3>
          <div className="table-toolbar">
            <select className="input" style={{ width: 180 }} value={actionFilter} onChange={(e) => setActionFilter(e.target.value)}>
              <option value="">All Actions</option>
              <option value="school.created">School Created</option>
              <option value="school.updated">School Updated</option>
              <option value="school.deleted">School Deleted</option>
              <option value="school.activated">School Activated</option>
              <option value="school.suspended">School Suspended</option>
              <option value="subscription.changed">Subscription Changed</option>
              <option value="password.reset">Password Reset</option>
            </select>
          </div>
        </div>
        <div className="table-responsive">
          <table className="data-table">
            <thead>
              <tr>
                <th>ID</th>
                <th>Action</th>
                <th>Resource</th>
                <th>Details</th>
                <th>User ID</th>
                <th>School ID</th>
                <th>IP Address</th>
                <th>Date/Time</th>
              </tr>
            </thead>
            <tbody>
              {logs.length === 0 ? (
                <tr>
                  <td colSpan={8}>
                    <div className="empty-state">
                      <div className="empty-state-icon">📋</div>
                      <h3>No audit logs found</h3>
                      <p>Actions performed across the platform will appear here.</p>
                    </div>
                  </td>
                </tr>
              ) : logs.map((log) => (
                <tr key={log.id}>
                  <td><code>{log.id}</code></td>
                  <td><span className={getActionColor(log.action)}>{log.action}</span></td>
                  <td>{log.resource || '-'}</td>
                  <td style={{ maxWidth: 300, overflow: 'hidden', textOverflow: 'ellipsis' }}>{log.details || '-'}</td>
                  <td>{log.user_id || '-'}</td>
                  <td>{log.school_id || '-'}</td>
                  <td><code>{log.ip_address || '-'}</code></td>
                  <td>{log.created_on ? new Date(log.created_on).toLocaleString() : '-'}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        <div className="table-footer">
          <span className="pagination-info">{logs.length} log{logs.length !== 1 ? 's' : ''}</span>
        </div>
      </div>
    </SuperAdminLayout>
  )
}