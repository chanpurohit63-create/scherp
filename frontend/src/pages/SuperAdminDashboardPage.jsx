import React, { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import SuperAdminLayout from '../components/SuperAdminLayout'
import { useAuth } from '../hooks/useAuth.jsx'
import { listResources } from '../api'
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, LineChart, Line, PieChart, Pie, Cell } from 'recharts'

const COLORS = ['#4f46e5', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6', '#ec4899', '#14b8a6']

export default function SuperAdminDashboardPage() {
  const auth = useAuth()
  const [data, setData] = useState(null)
  const [schools, setSchools] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    loadDashboard()
    loadSchools()
  }, [])

  const loadDashboard = async () => {
    try {
      const dashboardData = await listResources(auth.token, 'superadmin/platform/dashboard', 'skip=0&limit=100')
      setData(dashboardData)
    } catch (err) {
      console.error(err)
    }
  }

  const loadSchools = async () => {
    try {
      const data = await listResources(auth.token, 'superadmin/schools', 'skip=0&limit=1000')
      setSchools(data)
    } catch (err) {
      console.error(err)
    }
  }

  if (loading) {
    return (
      <SuperAdminLayout title="Dashboard">
        <div className="skeleton-grid">
          {Array.from({ length: 6 }).map((_, i) => <div key={i} className="skeleton-card" />)}
        </div>
        <div style={{ marginTop: 24 }}>
          <div className="skeleton-list">
            {Array.from({ length: 4 }).map((_, i) => <div key={i} className="skeleton-row" />)}
          </div>
        </div>
      </SuperAdminLayout>
    )
  }

  if (error) {
    return (
      <SuperAdminLayout title="Dashboard">
        <div className="error-banner">{error}</div>
      </SuperAdminLayout>
    )
  }

  // Calculate trial schools (free plan)
  const trialSchools = (data?.subscription_distribution || []).find(s => s.plan === 'free')?.count || 0

  // Calculate renewals (subscription_end within 30 days)
  const now = new Date()
  const thirtyDaysFromNow = new Date(now.getTime() + 30 * 24 * 60 * 60 * 1000)
  const renewals = schools.filter(s => {
    if (!s.subscription_end) return false
    const endDate = new Date(s.subscription_end)
    return endDate > now && endDate <= thirtyDaysFromNow
  }).length

  const widgets = [
    { label: 'Total Schools', value: data?.total_schools || 0, color: '#4f46e5', icon: '🏫', link: '/super-admin/schools' },
    { label: 'Active Schools', value: data?.active_schools || 0, color: '#10b981', icon: '✅', link: '/super-admin/schools' },
    { label: 'Expired Schools', value: data?.expired_schools || 0, color: '#ef4444', icon: '⏰', link: '/super-admin/schools' },
    { label: 'Total Revenue', value: `$${(data?.total_revenue || 0).toLocaleString()}`, color: '#14b8a6', icon: '💰', link: '/super-admin/payments' },
    { label: 'Trial Schools', value: trialSchools, color: '#f59e0b', icon: '🔄', link: '/super-admin/subscriptions' },
    { label: 'Renewals (30d)', value: renewals, color: '#8b5cf6', icon: '🔁', link: '/super-admin/subscriptions' },
  ]

  const schoolGrowth = data?.school_growth || []
  const revenueTrend = data?.revenue_trend || []
  const subDistribution = data?.subscription_distribution || []

  const schoolStatusData = [
    { name: 'Active', value: data?.active_schools || 0 },
    { name: 'Inactive', value: data?.inactive_schools || 0 },
    { name: 'Suspended', value: data?.suspended_schools || 0 },
    { name: 'Expired', value: data?.expired_schools || 0 },
  ].filter(d => d.value > 0)

  return (
    <SuperAdminLayout title="Platform Dashboard">
      <div className="welcome-banner">
        <div className="welcome-banner-content">
          <h2>Welcome, {auth.profile?.full_name || 'Super Admin'}</h2>
          <p>Platform overview and key metrics at a glance</p>
        </div>
        <div className="welcome-banner-actions">
          <Link to="/super-admin/schools" className="btn btn-primary">Manage Schools</Link>
        </div>
      </div>

      {/* Widget Grid */}
      <div className="metrics-grid">
        {widgets.map((w, i) => (
          <Link key={i} to={w.link} className="metric-card" style={{ borderTop: `3px solid ${w.color}`, textDecoration: 'none' }}>
            <div className="metric-icon" style={{ background: `${w.color}15`, color: w.color }}>{w.icon}</div>
            <span className="metric-label">{w.label}</span>
            <span className="metric-value">{w.value}</span>
          </Link>
        ))}
      </div>

      {/* Additional Stats */}
      <div className="stats-overview">
        <div className="stat-card">
          <div className="stat-icon" style={{ background: 'var(--primary-bg)', color: 'var(--primary)' }}>📅</div>
          <div className="stat-info">
            <div className="stat-label">New Schools This Month</div>
            <div className="stat-value">{data?.new_schools_this_month || 0}</div>
          </div>
        </div>
        <div className="stat-card">
          <div className="stat-icon" style={{ background: 'var(--success-bg)', color: 'var(--success)' }}>👤</div>
          <div className="stat-info">
            <div className="stat-label">Active Users Today</div>
            <div className="stat-value">{data?.active_users_today || 0}</div>
          </div>
        </div>
        <div className="stat-card">
          <div className="stat-icon" style={{ background: 'var(--purple-bg)', color: 'var(--purple)' }}>💵</div>
          <div className="stat-info">
            <div className="stat-label">Monthly Revenue</div>
            <div className="stat-value">${(data?.monthly_revenue || 0).toLocaleString()}</div>
          </div>
        </div>
        <div className="stat-card">
          <div className="stat-icon" style={{ background: 'var(--info-bg)', color: 'var(--info)' }}>👨‍🎓</div>
          <div className="stat-info">
            <div className="stat-label">Total Students</div>
            <div className="stat-value">{data?.total_students || 0}</div>
          </div>
        </div>
      </div>

      {/* Charts */}
      <div className="charts-grid">
        {schoolGrowth.length > 0 && (
          <div className="chart-card">
            <h3>School Growth (Monthly)</h3>
            <ResponsiveContainer width="100%" height={280}>
              <BarChart data={schoolGrowth}>
                <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
                <XAxis dataKey="month" tick={{ fontSize: 12 }} />
                <YAxis tick={{ fontSize: 12 }} />
                <Tooltip />
                <Bar dataKey="count" fill="#4f46e5" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        )}
        {revenueTrend.length > 0 && (
          <div className="chart-card">
            <h3>Revenue Trend</h3>
            <ResponsiveContainer width="100%" height={280}>
              <LineChart data={revenueTrend}>
                <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
                <XAxis dataKey="month" tick={{ fontSize: 12 }} />
                <YAxis tick={{ fontSize: 12 }} />
                <Tooltip />
                <Line type="monotone" dataKey="revenue" stroke="#10b981" strokeWidth={2} dot={{ fill: '#10b981', r: 4 }} />
              </LineChart>
            </ResponsiveContainer>
          </div>
        )}
        {schoolStatusData.length > 0 && (
          <div className="chart-card">
            <h3>School Status Distribution</h3>
            <ResponsiveContainer width="100%" height={280}>
              <PieChart>
                <Pie data={schoolStatusData} cx="50%" cy="50%" outerRadius={90} dataKey="value" label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}>
                  {schoolStatusData.map((_, i) => <Cell key={i} fill={COLORS[i % COLORS.length]} />)}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          </div>
        )}
        {subDistribution.length > 0 && (
          <div className="chart-card">
            <h3>Subscription Distribution</h3>
            <ResponsiveContainer width="100%" height={280}>
              <BarChart data={subDistribution} layout="vertical">
                <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
                <XAxis type="number" tick={{ fontSize: 12 }} />
                <YAxis dataKey="plan" type="category" tick={{ fontSize: 12 }} />
                <Tooltip />
                <Bar dataKey="count" fill="#8b5cf6" radius={[0, 4, 4, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        )}
      </div>

      {/* Quick Links */}
      <div className="quick-links">
        <Link to="/super-admin/schools" className="quick-link">
          <span className="quick-link-icon">🏫</span>
          Schools
        </Link>
        <Link to="/super-admin/subscriptions" className="quick-link">
          <span className="quick-link-icon">💳</span>
          Subscriptions
        </Link>
        <Link to="/super-admin/payments" className="quick-link">
          <span className="quick-link-icon">💰</span>
          Payments
        </Link>
        <Link to="/super-admin/audit-logs" className="quick-link">
          <span className="quick-link-icon">📋</span>
          Audit Logs
        </Link>
      </div>
    </SuperAdminLayout>
  )
}