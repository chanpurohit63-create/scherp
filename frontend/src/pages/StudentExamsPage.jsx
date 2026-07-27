import React, { useEffect, useState } from 'react'
import StudentLayout from '../components/StudentLayout'
import { useAuth } from '../hooks/useAuth.jsx'
import { listResources, downloadFile } from '../api'
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts'

export default function StudentExamsPage() {
  const auth = useAuth()
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => { loadExams() }, [])

  const loadExams = async () => {
    try {
      const d = await listResources(auth.token, 'portal/student/exams')
      setData(d)
    } catch (err) { console.error(err) }
    finally { setLoading(false) }
  }

  const handleDownloadReport = () => {
    downloadFile(auth.token, 'portal/student/exams/report-card', 'report_card.pdf')
  }

  if (loading) {
    return <StudentLayout title="Exams"><div className="skeleton-grid"><div className="skeleton-card" style={{ height: 200 }} /></div></StudentLayout>
  }

  // Group results by exam
  const examGroups = {}
  ;(data?.results || []).forEach((r) => {
    if (!examGroups[r.exam_name]) examGroups[r.exam_name] = []
    examGroups[r.exam_name].push(r)
  })

  const perfData = Object.entries(examGroups).map(([name, results]) => {
    const total = results.reduce((s, r) => s + (r.result.max_marks || 0), 0)
    const obtained = results.reduce((s, r) => s + (r.result.marks_obtained || 0), 0)
    return { name, pct: total ? Math.round((obtained / total) * 100) : 0 }
  })

  return (
    <StudentLayout title="Exams">
      <div className="metrics-grid">
        <div className="metric-card" style={{ borderTop: '3px solid #4f46e5' }}>
          <span className="metric-label">Total Obtained</span>
          <span className="metric-value">{data?.total_obtained || 0}</span>
        </div>
        <div className="metric-card" style={{ borderTop: '3px solid #10b981' }}>
          <span className="metric-label">Total Max</span>
          <span className="metric-value">{data?.total_max || 0}</span>
        </div>
        <div className="metric-card" style={{ borderTop: '3px solid #f59e0b' }}>
          <span className="metric-label">Percentage</span>
          <span className="metric-value">{data?.percentage || 0}%</span>
        </div>
        <div className="metric-card" style={{ borderTop: '3px solid #8b5cf6' }}>
          <span className="metric-label">GPA</span>
          <span className="metric-value">{data?.gpa || 0}</span>
        </div>
        <div className="metric-card" style={{ borderTop: '3px solid #ec4899' }}>
          <span className="metric-label">Class Rank</span>
          <span className="metric-value">{data?.rank || '-'}</span>
        </div>
      </div>

      {perfData.length > 0 && (
        <div className="chart-card">
          <h3>Performance Trend</h3>
          <ResponsiveContainer width="100%" height={250}>
            <BarChart data={perfData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="name" />
              <YAxis domain={[0, 100]} />
              <Tooltip />
              <Bar dataKey="pct" fill="#8b5cf6" />
            </BarChart>
          </ResponsiveContainer>
        </div>
      )}

      <div className="card" style={{ marginTop: 20 }}>
        <div className="list-header">
          <h3>Upcoming Exams</h3>
          <button className="btn btn-sm" onClick={handleDownloadReport}>Download Report Card</button>
        </div>
        {(data?.upcoming_exams || []).length > 0 ? (
          <div className="table-responsive">
            <table className="data-table">
              <thead>
                <tr><th>Exam Name</th><th>Start Date</th><th>End Date</th></tr>
              </thead>
              <tbody>
                {data.upcoming_exams.map((e) => (
                  <tr key={e.id}>
                    <td><strong>{e.name}</strong></td>
                    <td>{e.start_date}</td>
                    <td>{e.end_date || '-'}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : <div className="empty-state">No upcoming exams</div>}
      </div>

      <div className="card" style={{ marginTop: 20 }}>
        <h3>Exam Results</h3>
        {(data?.results || []).length > 0 ? (
          <div className="table-responsive">
            <table className="data-table">
              <thead>
                <tr><th>Exam</th><th>Subject</th><th>Marks</th><th>Max</th></tr>
              </thead>
              <tbody>
                {data.results.map((r, i) => (
                  <tr key={i}>
                    <td>{r.exam_name}</td>
                    <td>{r.subject_name}</td>
                    <td>{r.result.marks_obtained || '-'}</td>
                    <td>{r.result.max_marks || '-'}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : <div className="empty-state">No results yet</div>}
      </div>
    </StudentLayout>
  )
}
