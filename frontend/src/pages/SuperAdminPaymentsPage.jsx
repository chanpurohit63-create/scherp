import React, { useEffect, useState } from 'react'
import SuperAdminLayout from '../components/SuperAdminLayout'
import { useAuth } from '../hooks/useAuth.jsx'
import { listResources, getResource } from '../api'
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, BarChart, Bar } from 'recharts'
import toast from 'react-hot-toast'

export default function SuperAdminPaymentsPage() {
  const auth = useAuth()
  const [dashboard, setDashboard] = useState(null)
  const [schools, setSchools] = useState([])
  const [schoolStats, setSchoolStats] = useState({})
  const [loading, setLoading] = useState(true)
  const [search, setSearch] = useState('')

  useEffect(() => { loadData() }, [])

  const loadData = async () => {
    try {
      const [dashData, schoolsData] = await Promise.all([
        listResources(auth.token, 'superadmin/platform/dashboard'),
        listResources(auth.token, 'superadmin/schools?skip=0&limit=1000'),
      ])
      setDashboard(dashData)
      setSchools(schoolsData)
      
      // Load statistics for each school (limit to first 20 to avoid too many requests)
      const stats = {}
      await Promise.all(schoolsData.slice(0, 20).map(async (school) => {
        try {
          const stat = await getResource(auth.token, 'superadmin/schools', `${school.id}/statistics`)
          stats[school.id] = stat
        } catch (err) {
          // silent
        }
      }))
      setSchoolStats(stats)
    } catch (err) {
      console.error(err)
      toast.error('Failed to load payments data')
    } finally {
      setLoading(false)
    }
  }

  const filteredSchools = schools.filter(s => {
    if (search && !s.school_name.toLowerCase().includes(search.toLowerCase())) return false
    return true
  })

  if (loading) {
    return (
      <SuperAdminLayout title="Payments" breadcrumbs={[{ label: 'Payments', to: null }]}>
        <div className="skeleton-grid">
          {Array.from({ length: 4 }).map((_, i) => <div key={i} className="skeleton-card" />)}
        </div>
      </SuperAdminLayout>
    )
  }

  const revenueTrend = dashboard?.revenue_trend || []

  return (
    <SuperAdminLayout title="Payments" breadcrumbs={[{ label: 'Payments', to: null }]}>
      {/* Revenue Summary */}
      <div className="metrics-grid">
        <div className="metric-card" style={{ borderTop: '3px solid #10b981' }}>
          <div className="metric-icon" style={{ background: '#f0fdf4', color: '#10b981' }}>💰</div>
          <span className="metric-label">Total Revenue</span>
          <span className="metric-value">${(dashboard?.total_revenue || 0).toLocaleString()}</span>
        </div>
        <div className="metric-card" style={{ borderTop: '3px solid #4f46e5' }}>
          <div className="metric-icon" style={{ background: '#eef2ff', color: '#4f46e5' }}>💵</div>
          <span className="metric-label">Monthly Revenue</span>
          <span className="metric-value">${(dashboard?.monthly_revenue || 0).toLocaleString()}</span>
        </div>
        <div className="metric-card" style={{ borderTop: '3px solid #8b5cf6' }}>
          <div className="metric-icon" style={{ background: '#f5f3ff', color: '#8b5cf6' }}>🏫</div>
          <span className="metric-label">Active Schools</span>
          <span className="metric-value">{dashboard?.active_schools || 0}</span>
        </div>
        <div className="metric-card" style={{ borderTop: '3px solid #f59e0b' }}>
          <div className="metric-icon" style={{ background: '#fffbeb', color: '#f59e0b' }}>📊</div>
          <span className="metric-label">Avg Revenue/School</span>
          <span className="metric-value">${dashboard?.active_schools ? Math.round((dashboard?.total_revenue || 0) / dashboard.active_schools).toLocaleString() : 0}</span>
        </div>
      </div>

      {/* Revenue Chart */}
      {revenueTrend.length > 0 && (
        <div className="charts-grid">
          <div className="chart-card">
            <h3>Revenue Trend</h3>
            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={revenueTrend}>
                <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
                <XAxis dataKey="month" tick={{ fontSize: 12 }} />
                <YAxis tick={{ fontSize: 12 }} />
                <Tooltip formatter={(value) => `$${value.toLocaleString()}`} />
                <Line type="monotone" dataKey="revenue" stroke="#10b981" strokeWidth={3} dot={{ fill: '#10b981', r: 5 }} />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>
      )}

      {/* School Revenue Table */}
      <div className="table-container">
        <div className="table-header">
          <h3>Revenue by School</h3>
          <div className="table-toolbar">
            <input className="input search-input" placeholder="Search schools..." value={search} onChange={(e) => setSearch(e.target.value)} />
          </div>
        </div>
        <div className="table-responsive">
          <table className="data-table">
            <thead>
              <tr>
                <th>School</th>
                <th>Plan</th>
                <th>Students</th>
                <th>Teachers</th>
                <th>Parents</th>
                <th>Revenue</th>
                <th>Status</th>
              </tr>
            </thead>
            <tbody>
              {filteredSchools.length === 0 ? (
                <tr>
                  <td colSpan={7}>
                    <div className="empty-state">
                      <div className="empty-state-icon">💰</div>
                      <h3>No payment data found</h3>
                    </div>
                  </td>
                </tr>
              ) : filteredSchools.slice(0, 20).map((school) => {
                const stats = schoolStats[school.id] || {}
                return (
                  <tr key={school.id}>
                    <td><strong>{school.school_name}</strong></td>
                    <td><span className="badge badge-gray">{school.subscription_plan || 'free'}</span></td>
                    <td>{stats.total_students || '-'}</td>
                    <td>{stats.total_teachers || '-'}</td>
                    <td>{stats.total_parents || '-'}</td>
                    <td><strong>${(stats.total_revenue || 0).toLocaleString()}</strong></td>
                    <td>
                      <span className={`status-dot ${school.status}`}></span>
                      {school.status}
                    </td>
                  </tr>
                )
              })}
            </tbody>
          </table>
        </div>
        <div className="table-footer">
          <span className="pagination-info">
            Showing top 20 schools of {filteredSchools.length}
          </span>
        </div>
      </div>
    </SuperAdminLayout>
  )
}