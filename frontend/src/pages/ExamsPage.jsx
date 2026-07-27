import React, { useEffect, useState } from 'react'
import PageWrapper from '../components/PageWrapper'
import { useAuth } from '../hooks/useAuth.jsx'
import { listResources, createResource } from '../api'
import toast from 'react-hot-toast'

export default function ExamsPage() {
  const auth = useAuth()
  const [exams, setExams] = useState([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [form, setForm] = useState({ name: '', academic_year_id: '', start_date: '', end_date: '' })
  const [search, setSearch] = useState('')
  const [page, setPage] = useState(0)
  const pageSize = 10

  useEffect(() => { loadExams() }, [page, search])

  const buildQuery = () => {
    const params = new URLSearchParams({ skip: page * pageSize, limit: pageSize })
    if (search) params.set('query', search)
    return params.toString()
  }

  const loadExams = async () => {
    setLoading(true); setError('')
    try { const data = await listResources(auth.token, 'exams', buildQuery()); setExams(data) }
    catch (err) { setError(err.message) } finally { setLoading(false) }
  }

  const handleCreate = async (event) => {
    event.preventDefault(); setError('')
    const toastId = toast.loading('Creating exam...')
    try {
      await createResource(auth.token, 'exams', { name: form.name, academic_year_id: Number(form.academic_year_id), start_date: form.start_date || undefined, end_date: form.end_date || undefined })
      toast.success('Exam created!', { id: toastId })
      setForm({ name: '', academic_year_id: '', start_date: '', end_date: '' })
      await loadExams()
    } catch (err) { setError(err.message); toast.error(err.message, { id: toastId }) }
  }

  return (
    <PageWrapper title="Exams">
      <div className="card" style={{ marginBottom: 24 }}>
        <h2>Create Exam</h2>
        <form onSubmit={handleCreate} className="form-grid">
          <input className="input" value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} placeholder="Exam name" required />
          <input className="input" type="number" value={form.academic_year_id} onChange={(e) => setForm({ ...form, academic_year_id: e.target.value })} placeholder="Academic year ID" required />
          <input className="input" type="date" value={form.start_date} onChange={(e) => setForm({ ...form, start_date: e.target.value })} />
          <input className="input" type="date" value={form.end_date} onChange={(e) => setForm({ ...form, end_date: e.target.value })} />
          <button className="btn btn-primary" type="submit">Create</button>
        </form>
      </div>
      <div className="card">
        <div className="list-header">
          <h2>Exam List</h2>
          <input className="input search-input" placeholder="Search..." value={search} onChange={(e) => { setSearch(e.target.value); setPage(0) }} />
        </div>
        {loading ? (
          <div className="skeleton-list">{Array.from({ length: 5 }).map((_, i) => <div key={i} className="skeleton-row" />)}</div>
        ) : exams.length === 0 ? (
          <div className="empty-state">No exams found.</div>
        ) : (
          <div className="table-responsive">
            <table className="data-table">
              <thead><tr><th>ID</th><th>Name</th><th>Academic Year</th><th>Start</th><th>End</th></tr></thead>
              <tbody>
                {exams.map((exam) => (
                  <tr key={exam.id}>
                    <td>{exam.id}</td><td>{exam.name}</td><td>{exam.academic_year_id}</td><td>{exam.start_date}</td><td>{exam.end_date}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
        <div className="pagination">
          <button className="btn btn-sm" disabled={page === 0} onClick={() => setPage(page - 1)}>Previous</button>
          <span>Page {page + 1}</span>
          <button className="btn btn-sm" disabled={exams.length < pageSize} onClick={() => setPage(page + 1)}>Next</button>
        </div>
      </div>
      {error && <div className="error-banner">{error}</div>}
    </PageWrapper>
  )
}
