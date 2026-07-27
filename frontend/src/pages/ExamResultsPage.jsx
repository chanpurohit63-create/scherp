import React, { useEffect, useState } from 'react'
import PageWrapper from '../components/PageWrapper'
import { useAuth } from '../hooks/useAuth.jsx'
import { listResources, createResource, updateResource, deleteResource } from '../api'
import toast from 'react-hot-toast'

export default function ExamResultsPage() {
  const auth = useAuth()
  const [items, setItems] = useState([])
  const [exams, setExams] = useState([])
  const [subjects, setSubjects] = useState([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [page, setPage] = useState(0)
  const [editing, setEditing] = useState(null)
  const [form, setForm] = useState({ exam_id: '', student_id: '', subject_id: '', marks_obtained: '', max_marks: '' })
  const limit = 20

  useEffect(() => { load(); loadOptions() }, [page])

  const load = async () => {
    setLoading(true); setError('')
    try { setItems(await listResources(auth.token, 'exam-results', `skip=${page * limit}&limit=${limit}`)) }
    catch (err) { setError(err.message) } finally { setLoading(false) }
  }
  const loadOptions = async () => {
    try { setExams(await listResources(auth.token, 'exams')) } catch {}
    try { setSubjects(await listResources(auth.token, 'subjects')) } catch {}
  }

  const handleSubmit = async (e) => {
    e.preventDefault(); setError('')
    const toastId = toast.loading(editing ? 'Updating...' : 'Creating...')
    try {
      const body = { exam_id: Number(form.exam_id), student_id: Number(form.student_id), subject_id: Number(form.subject_id) }
      if (form.marks_obtained) body.marks_obtained = Number(form.marks_obtained)
      if (form.max_marks) body.max_marks = Number(form.max_marks)
      if (editing) { await updateResource(auth.token, 'exam-results', editing, body); toast.success('Updated!', { id: toastId }) }
      else { await createResource(auth.token, 'exam-results', body); toast.success('Created!', { id: toastId }) }
      setForm({ exam_id: '', student_id: '', subject_id: '', marks_obtained: '', max_marks: '' }); setEditing(null); await load()
    } catch (err) { setError(err.message); toast.error(err.message, { id: toastId }) }
  }

  const handleEdit = (item) => {
    setEditing(item.id)
    setForm({ exam_id: item.exam_id, student_id: item.student_id, subject_id: item.subject_id, marks_obtained: item.marks_obtained || '', max_marks: item.max_marks || '' })
  }
  const handleDelete = async (id) => {
    if (!window.confirm('Delete this result?')) return
    try { await deleteResource(auth.token, 'exam-results', id); toast.success('Deleted'); await load() }
    catch (err) { toast.error(err.message) }
  }

  const calculateGrade = (marks, max) => {
    if (!marks || !max) return '-'
    const pct = (marks / max) * 100
    if (pct >= 90) return 'A+'
    if (pct >= 80) return 'A'
    if (pct >= 70) return 'B+'
    if (pct >= 60) return 'B'
    if (pct >= 50) return 'C'
    if (pct >= 40) return 'D'
    return 'F'
  }

  return (
    <PageWrapper title="Exam Results">
      <div className="card" style={{ marginBottom: 24 }}>
        <h2>{editing ? 'Edit' : 'Create'} Exam Result</h2>
        <form onSubmit={handleSubmit} className="form-grid">
          <select className="input" value={form.exam_id} onChange={(e) => setForm({ ...form, exam_id: e.target.value })} required>
            <option value="">Select Exam</option>
            {exams.map((e) => <option key={e.id} value={e.id}>{e.name}</option>)}
          </select>
          <input className="input" type="number" value={form.student_id} onChange={(e) => setForm({ ...form, student_id: e.target.value })} placeholder="Student ID" required />
          <select className="input" value={form.subject_id} onChange={(e) => setForm({ ...form, subject_id: e.target.value })} required>
            <option value="">Select Subject</option>
            {subjects.map((s) => <option key={s.id} value={s.id}>{s.name}</option>)}
          </select>
          <input className="input" type="number" step="0.01" value={form.marks_obtained} onChange={(e) => setForm({ ...form, marks_obtained: e.target.value })} placeholder="Marks obtained" />
          <input className="input" type="number" step="0.01" value={form.max_marks} onChange={(e) => setForm({ ...form, max_marks: e.target.value })} placeholder="Max marks" />
          <div className="form-actions">
            <button className="btn btn-primary" type="submit">{editing ? 'Update' : 'Create'}</button>
            {editing && <button className="btn" type="button" onClick={() => { setEditing(null); setForm({ exam_id: '', student_id: '', subject_id: '', marks_obtained: '', max_marks: '' }) }}>Cancel</button>}
          </div>
        </form>
      </div>
      <div className="card">
        <h2>Results</h2>
        {loading ? <div className="skeleton-list">{Array.from({ length: 5 }).map((_, i) => <div key={i} className="skeleton-row" />)}</div>
        : items.length === 0 ? <div className="empty-state">No results found.</div>
        : <div className="table-responsive">
            <table className="data-table">
              <thead><tr><th>ID</th><th>Exam ID</th><th>Student ID</th><th>Subject ID</th><th>Marks</th><th>Max</th><th>Grade</th><th>Actions</th></tr></thead>
              <tbody>
                {items.map((item) => (
                  <tr key={item.id}>
                    <td>{item.id}</td><td>{item.exam_id}</td><td>{item.student_id}</td><td>{item.subject_id}</td>
                    <td>{item.marks_obtained ?? '-'}</td><td>{item.max_marks ?? '-'}</td>
                    <td><span className="role-badge">{calculateGrade(item.marks_obtained, item.max_marks)}</span></td>
                    <td className="action-cell">
                      <button className="btn btn-sm" onClick={() => handleEdit(item)}>Edit</button>
                      <button className="btn btn-sm btn-danger" onClick={() => handleDelete(item.id)}>Delete</button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>}
        <div className="pagination">
          <button className="btn btn-sm" disabled={page === 0} onClick={() => setPage(page - 1)}>Previous</button>
          <span>Page {page + 1}</span>
          <button className="btn btn-sm" disabled={items.length < limit} onClick={() => setPage(page + 1)}>Next</button>
        </div>
      </div>
      {error && <div className="error-banner">{error}</div>}
    </PageWrapper>
  )
}
