import React, { useEffect, useState } from 'react'
import { useParams } from 'react-router-dom'
import ParentLayout from '../components/ParentLayout'
import { useAuth } from '../hooks/useAuth.jsx'
import { listResources } from '../api'
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, PieChart, Pie, Cell, LineChart, Line } from 'recharts'

const COLORS = ['#4f46e5', '#10b981', '#f59e0b', '#ef4444']

export default function ParentProgressPage() {
  const auth = useAuth()
  const { studentId } = useParams()
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => { loadProgress() }, [studentId])

  const loadProgress = async () => {
    try {
      const d = await listResources(auth.token, `portal/parent/children/${studentId}/progress`)
      setData(d)
    } catch (err) { console.error(err) }
    finally { setLoading(false) }
  }

  if (loading) {
    return <ParentLayout title="Progress"><div className="skeleton-grid">{Array.from({ length: 4 }).map((_, i) => <div key={i} className="skeleton-card" />)}</div></ParentLayout>
  }

  const attTrend = (data?.attendance_trend || []).map((d) => ({
    name: ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'][d.month - 1],
    pct: d.pct
  })).filter(d => d.pct > 0)

  const academicTrend = (data?.academic_trend || [])

  const hwCompletion = data?.homework_completion || {}
  const hwData = [
    { name: 'Completed', value: hwCompletion.completed || 0 },
    { name: 'Pending', value: hwCompletion.pending || 0 },
    { name: 'Late', value: hwCompletion.late || 0 },
  ].filter(d => d.value > 0)

  const subjectPerf = (data?.subject_performance || [])

  return (
    <ParentLayout title="Progress Dashboard">
      <div className="charts-grid">
        {attTrend.length > 0 && (
          <div className="chart-card">
            <h3>Attendance Trend</h3>
            <ResponsiveContainer width="100%" height={250}>
              <LineChart data={attTrend}>
                <CartesianGrid strokeDasharray="3 3" /><XAxis dataKey="name" /><YAxis domain={[0, 100]} /><Tooltip />
                <Line type="monotone" dataKey="pct" stroke="#4f46e5" strokeWidth={2} />
              </LineChart>
            </ResponsiveContainer>
          </div>
        )}
        {academicTrend.length > 0 && (
          <div className="chart-card">
            <h3>Academic Performance</h3>
            <ResponsiveContainer width="100%" height={250}>
              <BarChart data={academicTrend}>
                <CartesianGrid strokeDasharray="3 3" /><XAxis dataKey="name" /><YAxis domain={[0, 100]} /><Tooltip />
                <Bar dataKey="pct" fill="#8b5cf6" />
              </BarChart>
            </ResponsiveContainer>
          </div>
        )}
        {hwData.length > 0 && (
          <div className="chart-card">
            <h3>Homework Completion</h3>
            <ResponsiveContainer width="100%" height={250}>
              <PieChart>
                <Pie data={hwData} cx="50%" cy="50%" innerRadius={60} outerRadius={90} dataKey="value" label>
                  {hwData.map((_, i) => <Cell key={i} fill={COLORS[i % COLORS.length]} />)}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          </div>
        )}
        {subjectPerf.length > 0 && (
          <div className="chart-card">
            <h3>Subject Performance</h3>
            <ResponsiveContainer width="100%" height={250}>
              <BarChart data={subjectPerf}>
                <CartesianGrid strokeDasharray="3 3" /><XAxis dataKey="name" /><YAxis domain={[0, 100]} /><Tooltip />
                <Bar dataKey="pct" fill="#10b981" />
              </BarChart>
            </ResponsiveContainer>
          </div>
        )}
      </div>
      {attTrend.length === 0 && academicTrend.length === 0 && hwData.length === 0 && subjectPerf.length === 0 && (
        <div className="empty-state">No progress data available yet</div>
      )}
    </ParentLayout>
  )
}
