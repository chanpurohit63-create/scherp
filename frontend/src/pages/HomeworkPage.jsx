import React, { useEffect, useState } from 'react'
import PageWrapper from '../components/PageWrapper'
import { useAuth } from '../hooks/useAuth.jsx'
import { listResources, createResource, updateResource, deleteResource, uploadFile } from '../api'
import toast from 'react-hot-toast'

export default function HomeworkPage() {
  const auth = useAuth()
  const [items, setItems] = useState([])
  const [submissions, setSubmissions] = useState([])
  const [classes, setClasses] = useState([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [page, setPage] = useState(0)
  const [tab, setTab] = useState('homework')
  const [editing, setEditing] = useState(null)
  const [form, setForm] = useState({ title: '', description: '', assigned_by: '', class_id: '', section_id: '', due_date: '' })
  const [subForm, setSubForm] = useState({ homework_id: '', student_id: '', remarks: '' })
  const limit = 20

  useEffect(() => { load(); loadClasses() }, [page])

  const load = async () => {
    setLoading(true); setError('')
    try {
      const q = `skip=${page * limit}&limit=${limit}`
      setItems(await listResources(auth.token, 'homeworks', q))
      setSubmissions(await listResources(auth.token, 'homework-submissions', q))
    } catch (err) { setError(err.message) } finally { setLoading(false) }
  }
  const loadClasses = async () => { try { setClasses(await listResources(auth.token, 'classes')) } catch {} }

  const handleSubmit = async (e) => {
    e.preventDefault(); setError('')
    const toastId = toast.loading(editing ? 'Updating...' : 'Creating...')
    try {
      const body = { ...form, assigned_by: Number(form.assigned_by), class_id: Number(form.class_id) }
      if (form.section_id) body.section_id = Number(form.section_id)
      if (form.due_date) body.due_date = form.due_date
      if (editing) { await updateResource(auth.token, 'homeworks', editing, body); toast.success('Updated!', { id: toastId }) }
      else { await createResource(auth.token, 'homeworks', body); toast.success('Created!', { id: toastId }) }
      setForm({ title: '', description: '', assigned_by: '', class_id: '', section_id: '', due_date: '' }); setEditing(null); await load()
    } catch (err) { setError(err.message); toast.error(err.message, { id: toastId }) }
  }

  const handleEdit = (item) => {
    setEditing(item.id); setForm({ title: item.title, description: item.description || '', assigned_by: item.assigned_by, class_id: item.class_id, section_id: item.section_id || '', due_date: item.due_date || '' })
  }

  const handleDelete = async (id) => {
    if (!window.confirm('Delete this homework?')) return
    try { await deleteResource(auth.token, 'homeworks', id); toast.success('Deleted'); await load() }
    catch (err) { toast.error(err.message) }
  }

  const handleGrade = async (id, grade, feedback) => {
    try { await updateResource(auth.token, 'homework-submissions', id, { grade, feedback }); toast.success('Graded'); await load() }
    catch (err) { toast.error(err.message) }
  }

  return (
    <PageWrapper title="Homework">
      <div className="tabs">
        <button className={`tab ${tab === 'homework' ? 'active' : ''}`} onClick={() => setTab('homework')}>Homework</button>
        <button className={`tab ${tab === 'submissions' ? 'active' : ''}`} onClick={() => setTab('submissions')}>Submissions</button>
      </div>

      {tab === 'homework' && (
        <>
          <div className="card" style={{ marginBottom: 24 }}>
            <h2>{editing ? 'Edit' : 'Create'} Homework</h2>
            <form onSubmit={handleSubmit} className="form-grid">
              <input className="input" value={form.title} onChange={(e) => setForm({ ...form, title: e.target.value })} placeholder="Title" required />
              <textarea className="input" value={form.description} onChange={(e) => setForm({ ...form, description: e.target.value })} placeholder="Description" rows={3} />
              <input className="input" type="number" value={form.assigned_by} onChange={(e) => setForm({ ...form, assigned_by: e.target.value })} placeholder="Teacher ID (assigned by)" required />
              <select className="input" value={form.class_id} onChange={(e) => setForm({ ...form, class_id: e.target.value })} required>
                <option value="">Select Class</option>
                {classes.map((c) => <option key={c.id} value={c.id}>{c.name}</option>)}
              </select>
              <input className="input" type="date" value={form.due_date} onChange={(e) => setForm({ ...form, due_date: e.target.value })} />
              <div className="form-actions">
                <button className="btn btn-primary" type="submit">{editing ? 'Update' : 'Create'}</button>
                {editing && <button className="btn" type="button" onClick={() => { setEditing(null); setForm({ title: '', description: '', assigned_by: '', class_id: '', section_id: '', due_date: '' }) }}>Cancel</button>}
              </div>
            </form>
          </div>
          <div className="card">
            <h2>Homework List</h2>
            {loading ? <div className="skeleton-list">{Array.from({ length: 5 }).map((_, i) => <div key={i} className="skeleton-row" />)}</div>
            : items.length === 0 ? <div className="empty-state">No homework found.</div>
            : <div className="table-responsive">
                <table className="data-table">
                  <thead><tr><th>ID</th><th>Title</th><th>Class</th><th>Due Date</th><th>Actions</th></tr></thead>
                  <tbody>
                    {items.map((item) => (
                      <tr key={item.id}>
                        <td>{item.id}</td><td>{item.title}</td><td>{item.class_id}</td><td>{item.due_date || '-'}</td>
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
        </>
      )}

      {tab === 'submissions' && (
        <div className="card">
          <h2>Submissions</h2>
          {loading ? <div className="skeleton-list">{Array.from({ length: 5 }).map((_, i) => <div key={i} className="skeleton-row" />)}</div>
          : submissions.length === 0 ? <div className="empty-state">No submissions found.</div>
          : <div className="table-responsive">
              <table className="data-table">
                <thead><tr><th>ID</th><th>Homework ID</th><th>Student ID</th><th>Status</th><th>Grade</th><th>Feedback</th><th>Actions</th></tr></thead>
                <tbody>
                  {submissions.map((sub) => (
                    <tr key={sub.id}>
                      <td>{sub.id}</td><td>{sub.homework_id}</td><td>{sub.student_id}</td><td>{sub.status}</td>
                      <td>
                        <input className="input" style={{ width: 60 }} defaultValue={sub.grade || ''} onBlur={(e) => handleGrade(sub.id, e.target.value, sub.feedback)} placeholder="Grade" />
                      </td>
                      <td>
                        <input className="input" style={{ width: 100 }} defaultValue={sub.feedback || ''} onBlur={(e) => handleGrade(sub.id, sub.grade, e.target.value)} placeholder="Feedback" />
                      </td>
                      <td className="action-cell"><button className="btn btn-sm" onClick={() => handleGrade(sub.id, sub.grade, sub.feedback)}>Save</button></td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>}
        </div>
      )}
      {error && <div className="error-banner">{error}</div>}
    </PageWrapper>
  )
}
