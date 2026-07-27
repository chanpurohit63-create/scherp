import React, { useEffect, useState } from 'react'
import TeacherLayout from '../components/TeacherLayout'
import { useAuth } from '../hooks/useAuth.jsx'
import { listResources, createResource, updateResource, deleteResource } from '../api'
import toast from 'react-hot-toast'

export default function TeacherHomeworkPage() {
  const auth = useAuth()
  const [homeworks, setHomeworks] = useState([])
  const [classes, setClasses] = useState([])
  const [selectedClass, setSelectedClass] = useState('')
  const [showForm, setShowForm] = useState(false)
  const [form, setForm] = useState({ title: '', description: '', class_id: '', section_id: '', due_date: '' })
  const [loading, setLoading] = useState(true)

  useEffect(() => { loadClasses() }, [])

  const loadClasses = async () => {
    try {
      const d = await listResources(auth.token, 'portal/teacher/classes')
      setClasses(d || [])
    } catch (err) { console.error(err) }
    finally { setLoading(false) }
  }

  const loadHomework = async (classId) => {
    try {
      const d = await listResources(auth.token, `portal/teacher/homework${classId ? `?class_id=${classId}` : ''}`)
      setHomeworks(d || [])
    } catch (err) { console.error(err) }
  }

  const handleCreate = async () => {
    if (!form.title || !form.class_id) { toast.error('Title and class required'); return }
    try {
      await createResource(auth.token, 'portal/teacher/homework', {
        title: form.title, description: form.description,
        class_id: parseInt(form.class_id), due_date: form.due_date || undefined,
        assigned_by: 0,
      })
      toast.success('Homework created')
      setShowForm(false)
      setForm({ title: '', description: '', class_id: '', section_id: '', due_date: '' })
      loadHomework(selectedClass)
    } catch (err) { toast.error('Create failed') }
  }

  const handleDelete = async (id) => {
    if (!confirm('Delete this homework?')) return
    try {
      await deleteResource(auth.token, 'portal/teacher/homework', id)
      toast.success('Deleted')
      loadHomework(selectedClass)
    } catch (err) { toast.error('Delete failed') }
  }

  if (loading) {
    return <TeacherLayout title="Homework"><div className="skeleton-card" style={{ height: 200 }} /></TeacherLayout>
  }

  return (
    <TeacherLayout title="Homework Management">
      <div className="filter-bar">
        <select className="input" value={selectedClass} onChange={(e) => { setSelectedClass(e.target.value); loadHomework(e.target.value) }}>
          <option value="">All classes</option>
          {classes.map((item) => (
            <option key={item.allocation.id} value={item.class.id}>{item.class.name} - {item.subject.name}</option>
          ))}
        </select>
        <button className="btn btn-primary" onClick={() => setShowForm(true)}>+ New Homework</button>
      </div>

      {showForm && (
        <div className="card" style={{ marginBottom: 16 }}>
          <h3>Create Homework</h3>
          <div className="form-grid">
            <label>Title <input className="input" value={form.title} onChange={(e) => setForm({ ...form, title: e.target.value })} /></label>
            <label>Description <textarea className="input" value={form.description} onChange={(e) => setForm({ ...form, description: e.target.value })} /></label>
            <label>Class <select className="input" value={form.class_id} onChange={(e) => setForm({ ...form, class_id: e.target.value })}>
              <option value="">Select class</option>
              {classes.map((item) => <option key={item.allocation.id} value={item.class.id}>{item.class.name}</option>)}
            </select></label>
            <label>Due Date <input className="input" type="date" value={form.due_date} onChange={(e) => setForm({ ...form, due_date: e.target.value })} /></label>
          </div>
          <div className="form-actions">
            <button className="btn btn-primary" onClick={handleCreate}>Save</button>
            <button className="btn" onClick={() => setShowForm(false)}>Cancel</button>
          </div>
        </div>
      )}

      <div className="card">
        <h3>Homework List</h3>
        {homeworks.length === 0 && <div className="empty-state">No homework assigned</div>}
        <div className="notice-list">
          {homeworks.map(({ homework, submission_count }) => (
            <div key={homework.id} className="notice-card">
              <div className="notice-header">
                <h3>{homework.title}</h3>
                <div className="action-cell">
                  <button className="btn btn-sm" onClick={() => handleDelete(homework.id)}>Delete</button>
                </div>
              </div>
              <div className="notice-content">{homework.description}</div>
              <div className="notice-meta">
                <span>Due: {homework.due_date ? new Date(homework.due_date).toLocaleDateString() : 'No date'}</span>
                <span>Submissions: {submission_count}</span>
              </div>
            </div>
          ))}
        </div>
      </div>
    </TeacherLayout>
  )
}

