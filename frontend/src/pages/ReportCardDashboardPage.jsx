import React, { useState, useEffect, useCallback } from 'react'
import { useAuth } from '../hooks/useAuth'
import {
  listReportCards, deleteReportCard, downloadReportCardPDF,
  bulkDownloadReportCardsPDF, getReportCardStats, listGradingRules
} from '../api'
import toast from 'react-hot-toast'

export default function ReportCardDashboardPage() {
  const { token } = useAuth()
  const [reportCards, setReportCards] = useState([])
  const [stats, setStats] = useState(null)
  const [loading, setLoading] = useState(true)
  const [selectedIds, setSelectedIds] = useState(new Set())
  const [filters, setFilters] = useState({
    academic_year_id: '',
    class_id: '',
    section_id: '',
    exam_id: '',
    search: '',
  })
  const [academicYears, setAcademicYears] = useState([])
  const [classes, setClasses] = useState([])
  const [sections, setSections] = useState([])
  const [exams, setExams] = useState([])

  const fetchData = useCallback(async () => {
    try {
      setLoading(true)
      const params = {}
      Object.entries(filters).forEach(([k, v]) => {
        if (v) params[k] = v
      })
      const [cards, statsData, years, clsList, secList, examList] = await Promise.all([
        listReportCards(token, params),
        getReportCardStats(token).catch(() => null),
        listReportCards(token, { limit: 1 }).then(() => fetch('/api/academic-years', { headers: { Authorization: `Bearer ${token}` } }).then(r => r.json()).catch(() => [])),
        fetch('/api/classes', { headers: { Authorization: `Bearer ${token}` } }).then(r => r.json()).catch(() => []),
        fetch('/api/sections', { headers: { Authorization: `Bearer ${token}` } }).then(r => r.json()).catch(() => []),
        fetch('/api/exams', { headers: { Authorization: `Bearer ${token}` } }).then(r => r.json()).catch(() => []),
      ])
      setReportCards(cards || [])
      setStats(statsData)
      setAcademicYears(years || [])
      setClasses(clsList || [])
      setSections(secList || [])
      setExams(examList || [])
    } catch (err) {
      toast.error('Failed to load report cards')
    } finally {
      setLoading(false)
    }
  }, [token, filters])

  useEffect(() => { fetchData() }, [fetchData])

  const handleDelete = async (id) => {
    if (!window.confirm('Delete this report card?')) return
    try {
      await deleteReportCard(token, id)
      toast.success('Report card deleted')
      fetchData()
    } catch (err) {
      toast.error('Delete failed')
    }
  }

  const handleDownload = async (id) => {
    try {
      await downloadReportCardPDF(token, id)
      toast.success('PDF downloaded')
    } catch (err) {
      toast.error('Download failed')
    }
  }

  const handleBulkDownload = async () => {
    if (selectedIds.size === 0) {
      toast.error('Select report cards to download')
      return
    }
    try {
      await bulkDownloadReportCardsPDF(token, Array.from(selectedIds))
      toast.success('ZIP downloaded')
    } catch (err) {
      toast.error('Bulk download failed')
    }
  }

  const toggleSelect = (id) => {
    const newSet = new Set(selectedIds)
    if (newSet.has(id)) newSet.delete(id)
    else newSet.add(id)
    setSelectedIds(newSet)
  }

  const selectAll = () => {
    if (selectedIds.size === reportCards.length) {
      setSelectedIds(new Set())
    } else {
      setSelectedIds(new Set(reportCards.map(r => r.id)))
    }
  }

  return (
    <div className="page-container">
      <div className="page-header">
        <h1>Report Cards</h1>
        <div className="header-actions">
          <a href="/report-cards/generate" className="btn btn-primary">Generate New</a>
          <a href="/report-cards/bulk-generate" className="btn btn-secondary">Bulk Generate</a>
          <a href="/grading-rules" className="btn btn-outline">Grading Rules</a>
        </div>
      </div>

      {stats && (
        <div className="stats-grid">
          <div className="stat-card">
            <div className="stat-value">{stats.total_report_cards || 0}</div>
            <div className="stat-label">Total Report Cards</div>
          </div>
          <div className="stat-card success">
            <div className="stat-value">{stats.passed || 0}</div>
            <div className="stat-label">Passed</div>
          </div>
          <div className="stat-card danger">
            <div className="stat-value">{stats.failed || 0}</div>
            <div className="stat-label">Failed</div>
          </div>
          <div className="stat-card info">
            <div className="stat-value">{stats.pass_percentage || 0}%</div>
            <div className="stat-label">Pass %</div>
          </div>
        </div>
      )}

      <div className="filter-bar">
        <select value={filters.academic_year_id} onChange={e => setFilters(f => ({ ...f, academic_year_id: e.target.value }))}>
          <option value="">All Academic Years</option>
          {academicYears.map(ay => <option key={ay.id} value={ay.id}>{ay.name}</option>)}
        </select>
        <select value={filters.class_id} onChange={e => setFilters(f => ({ ...f, class_id: e.target.value }))}>
          <option value="">All Classes</option>
          {classes.map(c => <option key={c.id} value={c.id}>{c.name}</option>)}
        </select>
        <select value={filters.section_id} onChange={e => setFilters(f => ({ ...f, section_id: e.target.value }))}>
          <option value="">All Sections</option>
          {sections.map(s => <option key={s.id} value={s.id}>{s.name}</option>)}
        </select>
        <select value={filters.exam_id} onChange={e => setFilters(f => ({ ...f, exam_id: e.target.value }))}>
          <option value="">All Exams</option>
          {exams.map(e => <option key={e.id} value={e.id}>{e.name}</option>)}
        </select>
        <input
          type="text"
          placeholder="Search student..."
          value={filters.search}
          onChange={e => setFilters(f => ({ ...f, search: e.target.value }))}
        />
        <button className="btn btn-sm" onClick={fetchData}>Search</button>
        {selectedIds.size > 0 && (
          <button className="btn btn-sm btn-secondary" onClick={handleBulkDownload}>
            Download Selected ({selectedIds.size})
          </button>
        )}
      </div>

      <div className="table-container">
        <table className="table">
          <thead>
            <tr>
              <th><input type="checkbox" checked={selectedIds.size === reportCards.length && reportCards.length > 0} onChange={selectAll} /></th>
              <th>Student</th>
              <th>Exam</th>
              <th>Academic Year</th>
              <th>Percentage</th>
              <th>Grade</th>
              <th>Result</th>
              <th>Generated</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {loading ? (
              <tr><td colSpan="9" className="text-center">Loading...</td></tr>
            ) : reportCards.length === 0 ? (
              <tr><td colSpan="9" className="text-center">No report cards found</td></tr>
            ) : reportCards.map(rc => (
              <tr key={rc.id}>
                <td><input type="checkbox" checked={selectedIds.has(rc.id)} onChange={() => toggleSelect(rc.id)} /></td>
                <td>
                  <a href={`/report-cards/${rc.id}/preview`} className="link">
                    Student #{rc.student_id}
                  </a>
                </td>
                <td>Exam #{rc.exam_id}</td>
                <td>AY #{rc.academic_year_id}</td>
                <td>{rc.percentage?.toFixed(2)}%</td>
                <td><span className="badge badge-primary">{rc.overall_grade || 'N/A'}</span></td>
                <td>
                  <span className={`badge ${rc.result_status === 'PASS' || rc.result_status === 'PROMOTED' ? 'badge-success' : rc.result_status === 'FAIL' ? 'badge-danger' : 'badge-warning'}`}>
                    {rc.result_status || 'N/A'}
                  </span>
                </td>
                <td>{rc.generated_on ? new Date(rc.generated_on).toLocaleDateString() : 'N/A'}</td>
                <td className="actions-cell">
                  <a href={`/report-cards/${rc.id}/preview`} className="btn btn-sm btn-outline" title="Preview">👁</a>
                  <button className="btn btn-sm btn-outline" onClick={() => handleDownload(rc.id)} title="Download PDF">📥</button>
                  <a href={`/report-cards/${rc.id}/regenerate`} className="btn btn-sm btn-outline" title="Regenerate">🔄</a>
                  <button className="btn btn-sm btn-danger" onClick={() => handleDelete(rc.id)} title="Delete">🗑</button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <style>{`
        .page-container { padding: 20px; max-width: 1400px; margin: 0 auto; }
        .page-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; }
        .page-header h1 { margin: 0; font-size: 24px; color: #1a2a3a; }
        .header-actions { display: flex; gap: 10px; }
        .stats-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px; margin-bottom: 20px; }
        .stat-card { background: white; border-radius: 10px; padding: 20px; box-shadow: 0 2px 8px rgba(0,0,0,0.08); text-align: center; }
        .stat-card.success { border-left: 4px solid #22c55e; }
        .stat-card.danger { border-left: 4px solid #ef4444; }
        .stat-card.info { border-left: 4px solid #3b82f6; }
        .stat-value { font-size: 28px; font-weight: 700; color: #1a2a3a; }
        .stat-label { font-size: 13px; color: #6b7280; margin-top: 5px; }
        .filter-bar { display: flex; gap: 10px; flex-wrap: wrap; margin-bottom: 20px; align-items: center; }
        .filter-bar select, .filter-bar input { padding: 8px 12px; border: 1px solid #d1d5db; border-radius: 6px; font-size: 13px; }
        .filter-bar input { min-width: 200px; }
        .table-container { background: white; border-radius: 10px; box-shadow: 0 2px 8px rgba(0,0,0,0.08); overflow-x: auto; }
        .table { width: 100%; border-collapse: collapse; }
        .table th { background: #f8fafc; padding: 12px 16px; text-align: left; font-size: 12px; font-weight: 600; color: #6b7280; text-transform: uppercase; border-bottom: 2px solid #e5e7eb; }
        .table td { padding: 12px 16px; border-bottom: 1px solid #f0f0f0; font-size: 14px; }
        .table tr:hover { background: #f8fafc; }
        .badge { display: inline-block; padding: 3px 10px; border-radius: 12px; font-size: 12px; font-weight: 500; }
        .badge-primary { background: #dbeafe; color: #1d4ed8; }
        .badge-success { background: #dcfce7; color: #16a34a; }
        .badge-danger { background: #fee2e2; color: #dc2626; }
        .badge-warning { background: #fef3c7; color: #d97706; }
        .actions-cell { display: flex; gap: 5px; }
        .btn { padding: 8px 16px; border-radius: 6px; border: none; cursor: pointer; font-size: 13px; font-weight: 500; text-decoration: none; display: inline-flex; align-items: center; gap: 5px; }
        .btn-primary { background: #1d4ed8; color: white; }
        .btn-secondary { background: #6b7280; color: white; }
        .btn-outline { background: transparent; border: 1px solid #d1d5db; color: #374151; }
        .btn-danger { background: #ef4444; color: white; }
        .btn-sm { padding: 5px 10px; font-size: 12px; }
        .link { color: #1d4ed8; text-decoration: none; }
        .link:hover { text-decoration: underline; }
        .text-center { text-align: center; color: #9ca3af; padding: 40px; }
      `}</style>
    </div>
  )
}