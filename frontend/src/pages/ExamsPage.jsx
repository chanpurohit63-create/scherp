import React, { useEffect, useState } from 'react'
import PageWrapper from '../components/PageWrapper'
import { useAuth } from '../hooks/useAuth'
import { listResources, createResource } from '../api'

export default function ExamsPage() {
  const auth = useAuth()
  const [exams, setExams] = useState([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [form, setForm] = useState({ name: '', academic_year_id: '', start_date: '', end_date: '' })

  useEffect(() => {
    loadExams()
  }, [])

  const loadExams = async () => {
    setLoading(true)
    setError('')
    try {
      const data = await listResources(auth.token, 'exams')
      setExams(data)
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  const handleCreate = async (event) => {
    event.preventDefault()
    setError('')
    try {
      await createResource(auth.token, 'exams', {
        name: form.name,
        academic_year_id: Number(form.academic_year_id),
        start_date: form.start_date || undefined,
        end_date: form.end_date || undefined,
      })
      setForm({ name: '', academic_year_id: '', start_date: '', end_date: '' })
      await loadExams()
    } catch (err) {
      setError(err.message)
    }
  }

  return (
    <PageWrapper title="Exams">
      <section style={{ marginBottom: 24 }}>
        <h2>Create Exam</h2>
        <form onSubmit={handleCreate} style={{ display: 'grid', gap: 12, maxWidth: 520 }}>
          <input value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} placeholder="Exam name" required />
          <input type="number" value={form.academic_year_id} onChange={(e) => setForm({ ...form, academic_year_id: e.target.value })} placeholder="Academic year ID" required />
          <input type="date" value={form.start_date} onChange={(e) => setForm({ ...form, start_date: e.target.value })} />
          <input type="date" value={form.end_date} onChange={(e) => setForm({ ...form, end_date: e.target.value })} />
          <button type="submit" style={{ padding: '10px 16px' }}>Create</button>
        </form>
      </section>

      <section>
        <h2>Exam List</h2>
        {loading ? (
          <p>Loading exams...</p>
        ) : (
          <table style={{ width: '100%', borderCollapse: 'collapse' }}>
            <thead>
              <tr>
                <th style={thStyle}>ID</th>
                <th style={thStyle}>Name</th>
                <th style={thStyle}>Academic Year</th>
                <th style={thStyle}>Start</th>
                <th style={thStyle}>End</th>
              </tr>
            </thead>
            <tbody>
              {exams.map((exam) => (
                <tr key={exam.id}>
                  <td style={tdStyle}>{exam.id}</td>
                  <td style={tdStyle}>{exam.name}</td>
                  <td style={tdStyle}>{exam.academic_year_id}</td>
                  <td style={tdStyle}>{exam.start_date}</td>
                  <td style={tdStyle}>{exam.end_date}</td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </section>
      {error && <p style={{ color: 'red' }}>{error}</p>}
    </PageWrapper>
  )
}

const thStyle = { borderBottom: '1px solid #ddd', padding: 8, textAlign: 'left' }
const tdStyle = { borderBottom: '1px solid #eee', padding: 8 }
