import React, { useEffect, useState } from 'react'
import PageWrapper from '../components/PageWrapper'
import { useAuth } from '../hooks/useAuth.jsx'
import { listResources, getBackendUrl } from '../api'
import toast from 'react-hot-toast'

const TABS = ['Students', 'Attendance', 'Teachers', 'Fees', 'Exams']

export default function ReportsPage() {
  const auth = useAuth()
  const [activeTab, setActiveTab] = useState('Students')
  const [data, setData] = useState([])
  const [loading, setLoading] = useState(false)
  const [query, setQuery] = useState('')
  const [statusFilter, setStatusFilter] = useState('')
  const [dateFrom, setDateFrom] = useState('')
  const [dateTo, setDateTo] = useState('')

  useEffect(() => {
    loadReport()
  }, [activeTab])

  const loadReport = async () => {
    setLoading(true)
    try {
      const path = `reports/${activeTab.toLowerCase()}`
      const params = new URLSearchParams({ skip: 0, limit: 100 })
      if (query) params.set('query', query)
      if (statusFilter) params.set(statusFilter.includes('paid') ? 'is_paid' : 'status', statusFilter)
      if (dateFrom) params.set('from_date', dateFrom)
      if (dateTo) params.set('to_date', dateTo)
      const result = await listResources(auth.token, path, params.toString())
      setData(Array.isArray(result) ? result : [])
    } catch (err) {
      toast.error('Failed to load report')
      setData([])
    } finally {
      setLoading(false)
    }
  }

  const handleExport = async (format) => {
    try {
      const path = `reports/${activeTab.toLowerCase()}`
      const params = new URLSearchParams({ skip: 0, limit: 1000, export: format })
      if (query) params.set('query', query)
      if (statusFilter) params.set(statusFilter.includes('paid') ? 'is_paid' : 'status', statusFilter)
      if (dateFrom) params.set('from_date', dateFrom)
      if (dateTo) params.set('to_date', dateTo)
      const url = `${getBackendUrl()}/api/${path}?${params.toString()}`
      const response = await fetch(url, { headers: { Authorization: `Bearer ${auth.token}` } })
      if (!response.ok) throw new Error('Export failed')
      const blob = await response.blob()
      const blobUrl = URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = blobUrl
      a.download = `${activeTab.toLowerCase()}_report.${format === 'csv' ? 'csv' : 'pdf'}`
      a.click()
      URL.revokeObjectURL(blobUrl)
    } catch (err) {
      toast.error(err.message)
    }
  }

  const renderTable = () => {
    if (loading) return <div className="skeleton-list">{Array.from({ length: 5 }).map((_, i) => <div key={i} className="skeleton-row" />)}</div>
    if (data.length === 0) return <div className="empty-state">No data found.</div>

    const cols = Object.keys(data[0] || {})
    return (
      <div className="table-responsive">
        <table className="data-table">
          <thead>
            <tr>{cols.map((c) => <th key={c}>{c.replace(/_/g, ' ').replace(/\b\w/g, (l) => l.toUpperCase())}</th>)}</tr>
          </thead>
          <tbody>
            {data.map((row, i) => (
              <tr key={i}>
                {cols.map((c) => <td key={c}>{String(row[c] ?? '')}</td>)}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    )
  }

  return (
    <PageWrapper title="Reports">
      <div className="tab-bar">
        {TABS.map((tab) => (
          <button key={tab} className={`tab ${activeTab === tab ? 'active' : ''}`} onClick={() => { setActiveTab(tab); setQuery(''); setStatusFilter(''); setDateFrom(''); setDateTo('') }}>{tab}</button>
        ))}
      </div>

      <div className="filter-bar">
        <input className="input" placeholder="Search..." value={query} onChange={(e) => setQuery(e.target.value)} />
        {activeTab === 'Attendance' && (
          <>
            <input className="input" type="date" value={dateFrom} onChange={(e) => setDateFrom(e.target.value)} placeholder="From" />
            <input className="input" type="date" value={dateTo} onChange={(e) => setDateTo(e.target.value)} placeholder="To" />
          </>
        )}
        {['Students', 'Fees'].includes(activeTab) && (
          <select className="input" value={statusFilter} onChange={(e) => setStatusFilter(e.target.value)}>
            <option value="">All</option>
            {activeTab === 'Students' && <><option value="active">Active</option><option value="inactive">Inactive</option></>}
            {activeTab === 'Fees' && <><option value="true">Paid</option><option value="false">Unpaid</option></>}
          </select>
        )}
        <button className="btn btn-primary" onClick={loadReport}>Search</button>
        <button className="btn" onClick={() => handleExport('csv')}>Export CSV</button>
      </div>

      {renderTable()}
    </PageWrapper>
  )
}

