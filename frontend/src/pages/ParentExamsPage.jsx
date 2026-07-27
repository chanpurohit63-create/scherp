import React, { useEffect, useState } from 'react'
import { useParams } from 'react-router-dom'
import ParentLayout from '../components/ParentLayout'
import { useAuth } from '../hooks/useAuth.jsx'
import { listResources, downloadFile } from '../api'
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts'

export default function ParentExamsPage() {
  const auth = useAuth()
  const { studentId } = useParams()
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => { loadResults() }, [studentId])

  const loadResults = async () => {
    try {
      const d = await listResources(auth.token, `portal/parent/children/${studentId}/results`)
      setData(d)
    } catch (err) { console.error(err) }
    finally { setLoading(false) }
  }

  const handleReportCard = () => {
    downloadFile(auth.token, `portal/parent/children/${studentId}/results/report-card`, 'report_card.pdf')
  }

  if (loading) {
    return <ParentLayout title="Results"><div className="skeleton-card" style={{ height: 200 }} /></ParentLayout>
  }

  const examGroups = {}
  ;(data?.results || []).forEach(({ result, subject, exam }) => {
    if (!examGroups[exam.name]) examGroups[exam.name] = []
    examGroups[exam.name].push({ result, subject, exam })
  })

  const perfData = Object.entries(examGroups).map(([name, items]) => {
    const total = items.reduce((s, i) => s + (i.result.max_marks || 0), 0)
    const obtained = items.reduce((s, i) => s + (i.result.marks_obtained || 0), 0)
    return { name, pct: total ? Math.round((obtained / total) * 100) : 0 }
  })

  return (
    <ParentLayout title="Results">
      <div className="metrics-grid">
        <div className="metric-card" style={{ borderTop: '3px solid #4f46e5' }}>
          <span className="metric-label">Total</span>
          <span className="metric-value">{data?.total_obtained || 0}/{data?.total_max || 0}</span>
        </div>
        <div className="metric-card" style={{ borderTop: '3px solid #10b981' }}>
          <span className="metric-label">Percentage</span>
          <span className="metric-value">{data?.percentage || 0}%</span>
        </div>
        <div className="metric-card" style={{ borderTop: '3px solid #f59e0b' }}>
          <span className="metric-label">GPA</span>
          <span className="metric-value">{data?.gpa || 0}</span>
        </div>
        <div className="metric-card" style={{ borderTop: '3px solid #8b5cf6' }}>
          <span className="metric-label">Download</span>
          <button className="btn btn-sm" onClick={handleReportCard}>Report Card</button>
        </div>
      </div>

      {perfData.length > 0 && (
        <div className="chart-card">
          <h3>Performance</h3>
          <ResponsiveContainer width="100%" height={250}>
            <BarChart data={perfData}>
              <CartesianGrid strokeDasharray="3 3" /><XAxis dataKey="name" /><YAxis domain={[0, 100]} /><Tooltip />
              <Bar dataKey="pct" fill="#8b5cf6" />
            </BarChart>
          </ResponsiveContainer>
        </div>
      )}

      <div className="card" style={{ marginTop: 20 }}>
        <h3>Subject-wise Results</h3>
        <div className="table-responsive">
          <table className="data-table">
            <thead><tr><th>Exam</th><th>Subject</th><th>Marks</th><th>Max</th></tr></thead>
            <tbody>
              {(data?.results || []).map((r, i) => (
                <tr key={i}>
                  <td>{r.exam.name}</td>
                  <td>{r.subject.name}</td>
                  <td>{r.result.marks_obtained || '-'}</td>
                  <td>{r.result.max_marks || '-'}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        {(!data?.results || data.results.length === 0) && <div className="empty-state">No results</div>}
      </div>
    </ParentLayout>
  )
}
