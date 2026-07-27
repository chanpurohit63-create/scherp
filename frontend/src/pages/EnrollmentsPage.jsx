import React, { useEffect, useState } from 'react'
import PageWrapper from '../components/PageWrapper'
import { useAuth } from '../hooks/useAuth.jsx'
import { listResources, createResource, deleteResource } from '../api'
import toast from 'react-hot-toast'

export default function EnrollmentsPage() {
  const auth = useAuth()
  const [items, setItems] = useState([])
  const [students, setStudents] = useState([])
  const [classes, setClasses] = useState([])
  const [sections, setSections] = useState([])
  const [years, setYears] = useState([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [page, setPage] = useState(0)
  const [form, setForm] = useState({ student_id: '', academic_year_id: '', class_id: '', section_id: '' })
  const limit = 20

  useEffect(() => { load(); loadOptions() }, [page])

  const load = async () => {
    setLoading(true); setError('')
    try { setItems(await listResources(auth.token, 'enrollments', `skip=${page * limit}&limit=${limit}`)) }
    catch (err) { setError(err.message) } finally { setLoading(false) }
  }
  const loadOptions = async () => {
    try { setStudents(await listResources(auth.token, 'students')) } catch {}
    try { setClasses(await listResources(auth.token, 'classes')) } catch {}
    try { setSections(await listResources(auth.token, 'sections')) } catch {}
    try { setYears(await listResources(auth.token, 'academic-years')) } catch {}
  }

  const handleSubmit = async (e) => {
    e.preventDefault(); setError('')
    const toastId = toast.loading('Enrolling...')
    try {
      const body = { student_id: Number(form.student_id), academic_year_id: Number(form.academic_year_id), class_id: Number(form.class_id) }
      if (form.section_id) body.section_id = Number(form.section_id)
      await createResource(auth.token, 'enrollments', body)
      toast.success('Enrolled!', { id: toastId })
      setForm({ student_id: '', academic_year_id: '', class_id: '', section_id: '' }); await load()
    } catch (err) { setError(err.message); toast.error(err.message, { id: toastId }) }
  }

  const handleDelete = async (id) => {
    if (!window.confirm('Delete this enrollment?')) return
    try { await deleteResource(auth.token, 'enrollments', id); toast.success('Deleted'); await load() }
    catch (err) { toast.error(err.message) }
  }

  return (
    <PageWrapper title="Enrollments">
      <div className="card" style={{ marginBottom: 24 }}>
        <h2>New Enrollment</h2>
        <form onSubmit={handleSubmit} className="form-grid">
          <select className="input" value={form.student_id} onChange={(e) => setForm({ ...form, student_id: e.target.value })} required>
            <option value="">Select Student ID</option>
            {students.map((s) => <option key={s.id} value={s.id}>Student #{s.id} ({s.admission_no || ''})</option>)}
          </select>
          <select className="input" value={form.academic_year_id} onChange={(e) => setForm({ ...form, academic_year_id: e.target.value })} required>
            <option value="">Select Academic Year</option>
            {years.map((y) => <option key={y.id} value={y.id}>{y.name}</option>)}
          </select>
          <select className="input" value={form.class_id} onChange={(e) => setForm({ ...form, class_id: e.target.value })} required>
            <option value="">Select Class</option>
            {classes.map((c) => <option key={c.id} value={c.id}>{c.name}</option>)}
          </select>
          <select className="input" value={form.section_id} onChange={(e) => setForm({ ...form, section_id: e.target.value })}>
            <option value="">No Section</option>
            {sections.map((s) => <option key={s.id} value={s.id}>{s.name}</option>)}
          </select>
          <button className="btn btn-primary" type="submit">Enroll</button>
        </form>
      </div>
      <div className="card">
        <h2>Enrollments</h2>
        {loading ? <div className="skeleton-list">{Array.from({ length: 5 }).map((_, i) => <div key={i} className="skeleton-row" />)}</div>
        : items.length === 0 ? <div className="empty-state">No enrollments found.</div>
        : <div className="table-responsive">
            <table className="data-table">
              <thead><tr><th>ID</th><th>Student ID</th><th>Year ID</th><th>Class ID</th><th>Section ID</th><th>Enrolled On</th><th>Actions</th></tr></thead>
              <tbody>
                {items.map((item) => (
                  <tr key={item.id}>
                    <td>{item.id}</td><td>{item.student_id}</td><td>{item.academic_year_id}</td><td>{item.class_id}</td><td>{item.section_id || '-'}</td><td>{new Date(item.enrolled_on).toLocaleDateString()}</td>
                    <td className="action-cell"><button className="btn btn-sm btn-danger" onClick={() => handleDelete(item.id)}>Delete</button></td>
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
