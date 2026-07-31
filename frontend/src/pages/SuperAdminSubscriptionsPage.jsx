import React, { useEffect, useState } from 'react'
import SuperAdminLayout from '../components/SuperAdminLayout'
import { useAuth } from '../hooks/useAuth.jsx'
import { listResources, createResource } from '../api'
import { BACKEND_URL } from '../api'
import { PieChart, Pie, Cell, Tooltip, ResponsiveContainer, BarChart, Bar, XAxis, YAxis, CartesianGrid } from 'recharts'
import toast from 'react-hot-toast'

const COLORS = ['#4f46e5', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6']
const PLANS = ['free', 'basic', 'standard', 'premium']

export default function SuperAdminSubscriptionsPage() {
  const auth = useAuth()
  const [schools, setSchools] = useState([])
  const [dashboard, setDashboard] = useState(null)
  const [loading, setLoading] = useState(true)
  const [search, setSearch] = useState('')
  const [planFilter, setPlanFilter] = useState('')
  const [editSchool, setEditSchool] = useState(null)
  const [subForm, setSubForm] = useState({ plan: 'free', subscription_start: '', subscription_end: '' })

  useEffect(() => { loadData() }, [])

  const loadData = async () => {
    try {
      const [schoolsData, dashData] = await Promise.all([
        listResources(auth.token, 'superadmin/schools?skip=0&limit=1000'),
        listResources(auth.token, 'superadmin/platform/dashboard'),
      ])
      setSchools(schoolsData)
      setDashboard(dashData)
    } catch (err) {
      console.error(err)
      toast.error('Failed to load subscriptions')
    } finally {
      setLoading(false)
    }
  }

  const handleUpdateSubscription = async (e) => {
    e.preventDefault()
    try {
      const params = new URLSearchParams()
      params.append('plan', subForm.plan)
      if (subForm.subscription_start) params.append('subscription_start', subForm.subscription_start)
      if (subForm.subscription_end) params.append('subscription_end', subForm.subscription_end)
      await fetch(`${BACKEND_URL}/api/superadmin/schools/${editSchool.id}/subscription?${params.toString()}`, {
        method: 'PUT',
        headers: { Authorization: `Bearer ${auth.token}` },
      })
      toast.success('Subscription updated successfully!')
      setEditSchool(null)
      setSubForm({ plan: 'free', subscription_start: '', subscription_end: '' })
      loadData()
    } catch (err) {
      toast.error(err.message || 'Failed to update subscription')
    }
  }

  const openEditModal = (school) => {
    setEditSchool(school)
    setSubForm({
      plan: school.subscription_plan || 'free',
      subscription_start: school.subscription_start || '',
      subscription_end: school.subscription_end || '',
    })
  }

  const getPlanBadge = (plan) => {
    const map = {
      free: 'badge badge-gray',
      basic: 'badge badge-info',
      standard: 'badge badge-primary',
      premium: 'badge badge-purple',
    }
    return <span className={map[plan] || 'badge badge-gray'}>{plan || 'free'}</span>
  }

  const filteredSchools = schools.filter(s => {
    if (search && !s.school_name.toLowerCase().includes(search.toLowerCase()) && !s.school_code.toLowerCase().includes(search.toLowerCase())) return false
    if (planFilter && s.subscription_plan !== planFilter) return false
    return true
  })

  const now = new Date()
  const thirtyDaysFromNow = new Date(now.getTime() + 30 * 24 * 60 * 60 * 1000)
  const renewals = schools.filter(s => s.subscription_end && new Date(s.subscription_end) > now && new Date(s.subscription_end) <= thirtyDaysFromNow)
  const expired = schools.filter(s => s.subscription_end && new Date(s.subscription_end) < now)

  const subDistribution = dashboard?.subscription_distribution || []

  if (loading) {
    return (
      <SuperAdminLayout title="Subscriptions" breadcrumbs={[{ label: 'Subscriptions', to: null }]}>
        <div className="skeleton-grid">
          {Array.from({ length: 4 }).map((_, i) => <div key={i} className="skeleton-card" />)}
        </div>
      </SuperAdminLayout>
    )
  }

  return (
    <SuperAdminLayout title="Subscriptions" breadcrumbs={[{ label: 'Subscriptions', to: null }]}>
      {/* Summary Cards */}
      <div className="metrics-grid">
        <div className="metric-card" style={{ borderTop: '3px solid #4f46e5' }}>
          <div className="metric-icon" style={{ background: '#eef2ff', color: '#4f46e5' }}>🏫</div>
          <span className="metric-label">Total Schools</span>
          <span className="metric-value">{schools.length}</span>
        </div>
        <div className="metric-card" style={{ borderTop: '3px solid #f59e0b' }}>
          <div className="metric-icon" style={{ background: '#fffbeb', color: '#f59e0b' }}>🔄</div>
          <span className="metric-label">Trial (Free)</span>
          <span className="metric-value">{schools.filter(s => s.subscription_plan === 'free').length}</span>
        </div>
        <div className="metric-card" style={{ borderTop: '3px solid #8b5cf6' }}>
          <div className="metric-icon" style={{ background: '#f5f3ff', color: '#8b5cf6' }}>🔁</div>
          <span className="metric-label">Renewals (30d)</span>
          <span className="metric-value">{renewals.length}</span>
        </div>
        <div className="metric-card" style={{ borderTop: '3px solid #ef4444' }}>
          <div className="metric-icon" style={{ background: '#fef2f2', color: '#ef4444' }}>⏰</div>
          <span className="metric-label">Expired</span>
          <span className="metric-value">{expired.length}</span>
        </div>
      </div>

      {/* Charts */}
      {subDistribution.length > 0 && (
        <div className="charts-grid">
          <div className="chart-card">
            <h3>Subscription Distribution</h3>
            <ResponsiveContainer width="100%" height={280}>
              <PieChart>
                <Pie data={subDistribution} cx="50%" cy="50%" outerRadius={90} dataKey="count" nameKey="plan" label={({ plan, percent }) => `${plan} ${(percent * 100).toFixed(0)}%`}>
                  {subDistribution.map((_, i) => <Cell key={i} fill={COLORS[i % COLORS.length]} />)}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          </div>
          <div className="chart-card">
            <h3>Plan Comparison</h3>
            <ResponsiveContainer width="100%" height={280}>
              <BarChart data={subDistribution}>
                <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
                <XAxis dataKey="plan" tick={{ fontSize: 12 }} />
                <YAxis tick={{ fontSize: 12 }} />
                <Tooltip />
                <Bar dataKey="count" fill="#8b5cf6" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      )}

      {/* Schools Table */}
      <div className="table-container">
        <div className="table-header">
          <h3>School Subscriptions</h3>
          <div className="table-toolbar">
            <input className="input search-input" placeholder="Search schools..." value={search} onChange={(e) => setSearch(e.target.value)} />
            <select className="input" style={{ width: 140 }} value={planFilter} onChange={(e) => setPlanFilter(e.target.value)}>
              <option value="">All Plans</option>
              <option value="free">Free</option>
              <option value="basic">Basic</option>
              <option value="standard">Standard</option>
              <option value="premium">Premium</option>
            </select>
          </div>
        </div>
        <div className="table-responsive">
          <table className="data-table">
            <thead>
              <tr>
                <th>School</th>
                <th>Code</th>
                <th>Plan</th>
                <th>Start Date</th>
                <th>End Date</th>
                <th>Status</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {filteredSchools.length === 0 ? (
                <tr>
                  <td colSpan={7}>
                    <div className="empty-state">
                      <div className="empty-state-icon">💳</div>
                      <h3>No schools found</h3>
                    </div>
                  </td>
                </tr>
              ) : filteredSchools.map((school) => {
                const isExpired = school.subscription_end && new Date(school.subscription_end) < now
                const isRenewal = school.subscription_end && new Date(school.subscription_end) > now && new Date(school.subscription_end) <= thirtyDaysFromNow
                return (
                  <tr key={school.id}>
                    <td><strong>{school.school_name}</strong></td>
                    <td><code>{school.school_code}</code></td>
                    <td>{getPlanBadge(school.subscription_plan)}</td>
                    <td>{school.subscription_start ? new Date(school.subscription_start).toLocaleDateString() : '-'}</td>
                    <td>
                      {school.subscription_end ? new Date(school.subscription_end).toLocaleDateString() : '-'}
                      {isExpired && <span className="badge badge-danger" style={{ marginLeft: 6 }}>Expired</span>}
                      {isRenewal && <span className="badge badge-warning" style={{ marginLeft: 6 }}>Renew Soon</span>}
                    </td>
                    <td>
                      <span className={`status-dot ${school.status}`}></span>
                      {school.status}
                    </td>
                    <td>
                      <button className="btn btn-sm btn-primary" onClick={() => openEditModal(school)}>Edit Plan</button>
                    </td>
                  </tr>
                )
              })}
            </tbody>
          </table>
        </div>
        <div className="table-footer">
          <span className="pagination-info">{filteredSchools.length} school{filteredSchools.length !== 1 ? 's' : ''}</span>
        </div>
      </div>

      {/* Edit Subscription Modal */}
      {editSchool && (
        <div className="modal-overlay" onClick={() => setEditSchool(null)}>
          <div className="modal" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h2>Edit Subscription - {editSchool.school_name}</h2>
              <button className="modal-close" onClick={() => setEditSchool(null)}>✕</button>
            </div>
            <form onSubmit={handleUpdateSubscription}>
              <div className="modal-body">
                <div className="form-grid">
                  <div className="form-group" style={{ gridColumn: 'span 2' }}>
                    <label>Subscription Plan *</label>
                    <select className="input" value={subForm.plan} onChange={(e) => setSubForm({ ...subForm, plan: e.target.value })}>
                      <option value="free">Free</option>
                      <option value="basic">Basic</option>
                      <option value="standard">Standard</option>
                      <option value="premium">Premium</option>
                    </select>
                  </div>
                  <div className="form-group">
                    <label>Start Date</label>
                    <input className="input" type="date" value={subForm.subscription_start} onChange={(e) => setSubForm({ ...subForm, subscription_start: e.target.value })} />
                  </div>
                  <div className="form-group">
                    <label>End Date</label>
                    <input className="input" type="date" value={subForm.subscription_end} onChange={(e) => setSubForm({ ...subForm, subscription_end: e.target.value })} />
                  </div>
                </div>
              </div>
              <div className="modal-footer">
                <button type="button" className="btn" onClick={() => setEditSchool(null)}>Cancel</button>
                <button type="submit" className="btn btn-primary">Update Subscription</button>
              </div>
            </form>
          </div>
        </div>
      )}
    </SuperAdminLayout>
  )
}