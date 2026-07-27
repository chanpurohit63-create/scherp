import React, { useEffect, useState } from 'react'
import StudentLayout from '../components/StudentLayout'
import { useAuth } from '../hooks/useAuth.jsx'
import { listResources, downloadFile } from '../api'
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts'

export default function StudentAttendancePage() {
  const auth = useAuth()
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => { loadAttendance() }, [])

  const loadAttendance = async () => {
    try {
      const d = await listResources(auth.token, 'portal/student/attendance')
      setData(d)
    } catch (err) { console.error(err) }
    finally { setLoading(false) }
  }

  const handleDownload = () => {
    downloadFile(auth.token, 'portal/student/attendance/download', 'attendance.csv')
  }

  if (loading) {
    return <StudentLayout title="Attendance"><div className="skeleton-grid"><div className="skeleton-card" style={{ height: 200 }} /></div></StudentLayout>
  }

  const monthlyData = (data?.monthly || []).map((d) => ({
    name: ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'][d.month - 1],
    present: d.present,
    absent: d.total - d.present,
  }))

  return (
    <StudentLayout title="Attendance">
      <div className="metrics-grid">
        <div className="metric-card" style={{ borderTop: '3px solid #4f46e5' }}>
          <span className="metric-label">Total Days</span>
          <span className="metric-value">{data?.total || 0}</span>
        </div>
        <div className="metric-card" style={{ borderTop: '3px solid #10b981' }}>
          <span className="metric-label">Present</span>
          <span className="metric-value">{data?.present || 0}</span>
        </div>
        <div className="metric-card" style={{ borderTop: '3px solid #ef4444' }}>
          <span className="metric-label">Absent</span>
          <span className="metric-value">{data?.absent || 0}</span>
        </div>
        <div className="metric-card" style={{ borderTop: '3px solid #f59e0b' }}>
          <span className="metric-label">Percentage</span>
          <span className="metric-value">{data?.percentage || 0}%</span>
        </div>
      </div>

      <div className="charts-grid">
        <div className="chart-card">
          <h3>Monthly Attendance Trend</h3>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={monthlyData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="name" />
              <YAxis />
              <Tooltip />
              <Bar dataKey="present" fill="#4f46e5" stackId="a" />
              <Bar dataKey="absent" fill="#f1f5f9" stackId="a" />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      <div className="card" style={{ marginTop: 20 }}>
        <div className="list-header">
          <h3>Attendance Records</h3>
          <button className="btn btn-sm" onClick={handleDownload}>Download CSV</button>
        </div>
        <div className="table-responsive">
          <table className="data-table">
            <thead>
              <tr>
                <th>Date</th>
                <th>Status</th>
                <th>Remarks</th>
              </tr>
            </thead>
            <tbody>
              {(data?.records || []).map((r) => (
                <tr key={r.id}>
                  <td>{r.date}</td>
                  <td><span className={`role-badge ${r.status === 'present' ? '' : ''}`} style={{ background: r.status === 'present' ? '#d1fae5' : '#fee2e2', color: r.status === 'present' ? '#065f46' : '#991b1b' }}>{r.status}</span></td>
                  <td>{r.remarks || '-'}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        {(!data?.records || data.records.length === 0) && <div className="empty-state">No attendance records</div>}
      </div>
    </StudentLayout>
  )
}
