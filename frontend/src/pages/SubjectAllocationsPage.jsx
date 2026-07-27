import React, { useEffect, useState } from 'react'
import PageWrapper from '../components/PageWrapper'
import { useAuth } from '../hooks/useAuth.jsx'
import { listResources, createResource, updateResource, deleteResource } from '../api'
import toast from 'react-hot-toast'

export default function SubjectAllocationsPage() {
  const auth = useAuth()
  const [items, setItems] = useState([])
  const [subjects, setSubjects] = useState([])
  const [teachers, setTeachers] = useState([])
  const [classes, setClasses] = useState([])
  const [sections, setSections] = useState([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [page, setPage] = useState(0)
  const [editing, setEditing] = useState(null)
  const [form, setForm] = useState({ subject_id: '', teacher_id: '', class_id: '', section_id: '' })
  const limit = 20

  useEffect(() => { load(); loadOptions() }, [page])

  const load = async () => {
    setLoading(true); setError('')
    try { setItems(await listResources(auth.token, 'subject-allocations', `skip=${page * limit}&limit=${limit}`)) }
    catch (err) { setError(err.message) } finally { setLoading(false) }
  }
  const loadOptions = async () => {
    try { setSubjects(await listResources(auth.token, 'subjects')) } catch {}
    try { setTeachers(await listResources(auth.token, 'teachers')) } catch {}
    try { setClasses(await listResources(auth.token, 'classes')) } catch {}
    try { setSections(await listResources(auth.token, 'sections')) } catch {}
  }

  const handleSubmit = async (e) => {
    e.preventDefault(); setError('')
    const toastId = toast.loading(editing ? 'Updating...' : 'Creating...')
    try {
      const body = { subject_id: Number(form.subject_id), teacher_id: Number(form.teacher_id), class_id: Number(form.class_id) }
      if (form.section_id) body.section_id = Number(form.section_id)
      if (editing) { await updateResource(auth.token, 'subject-allocations', editing, body); toast.success('Updated!', { id: toastId }) }
      else { await createResource(auth.token, 'subject-allocations', body); toast.success('Created!', { id: toastId }) }
      setForm({ subject_id: '', teacher_id: '', class_id: '', section_id: '' }); setEditing(null); await load()
    } catch (err) { setError(err.message); toast.error(err.message, { id: toastId }) }
  }

  const handleEdit = (item) => { setEditing(item.id); setForm({ subject_id: item.subject_id, teacher_id: item.teacher_id, class_id: item.class_id, section_id: item.section_id || '' }) }
  const handleDelete = async (id) => {
    if (!window.confirm('Delete this allocation?')) return
    try { await deleteResource(auth.token, 'subject-allocations', id); toast.success('Deleted'); await load() }
    catch (err) { toast.error(err.message) }
  }

  return (
    <PageWrapper title="Subject Allocations">
      <div className="card" style={{ marginBottom: 24 }}>
        <h2>{editing ? 'Edit' : 'Create'} Allocation</h2>
        <form onSubmit={handleSubmit} className="form-grid">
          <select className="input" value={form.subject_id} onChange={(e) => setForm({ ...form, subject_id: e.target.value })} required>
            <option value="">Select Subject</option>
            {subjects.map((s) => <option key={s.id} value={s.id}>{s.name}</option>)}
          </select>
          <select className="input" value={form.teacher_id} onChange={(e) => setForm({ ...form, teacher_id: e.target.value })} required>
            <option value="">Select Teacher ID</option>
            {teachers.map((t) => <option key={t.id} value={t.id}>Teacher #{t.id}</option>)}
          </select>
          <select className="input" value={form.class_id} onChange={(e) => setForm({ ...form, class_id: e.target.value })} required>
            <option value="">Select Class</option>
            {classes.map((c) => <option key={c.id} value={c.id}>{c.name}</option>)}
          </select>
          <select className="input" value={form.section_id} onChange={(e) => setForm({ ...form, section_id: e.target.value })}>
            <option value="">No Section</option>
            {sections.map((s) => <option key={s.id} value={s.id}>{s.name}</option>)}
          </select>
          <div className="form-actions">
            <button className="btn btn-primary" type="submit">{editing ? 'Update' : 'Create'}</button>
            {editing && <button className="btn" type="button" onClick={() => { setEditing(null); setForm({ subject_id: '', teacher_id: '', class_id: '', section_id: '' }) }}>Cancel</button>}
          </div>
        </form>
      </div>
      <div className="card">
        <h2>Allocations</h2>
        {loading ? <div className="skeleton-list">{Array.from({ length: 5 }).map((_, i) => <div key={i} className="skeleton-row" />)}</div>
        : items.length === 0 ? <div className="empty-state">No allocations found.</div>
        : <div className="table-responsive">
            <table className="data-table">
              <thead><tr><th>ID</th><th>Subject ID</th><th>Teacher ID</th><th>Class ID</th><th>Section ID</th><th>Actions</th></tr></thead>
              <tbody>
                {items.map((item) => (
                  <tr key={item.id}>
                    <td>{item.id}</td><td>{item.subject_id}</td><td>{item.teacher_id}</td><td>{item.class_id}</td><td>{item.section_id || '-'}</td>
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
