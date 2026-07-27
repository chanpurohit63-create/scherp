import React, { useEffect, useState } from 'react'
import TeacherLayout from '../components/TeacherLayout'
import { useAuth } from '../hooks/useAuth.jsx'
import { listResources, createResource, updateResource, deleteResource } from '../api'
import toast from 'react-hot-toast'

export default function TeacherExamsPage() {
  const auth = useAuth()
  const [exams, setExams] = useState([])
  const [showForm, setShowForm] = useState(false)
  const [form, setForm] = useState({ name: '', academic_year_id: 1, start_date: '', end_date: '' })
  const [loading, setLoading] = useState(true)

  useEffect(() => { loadExams() }, [])

  const loadExams = async () => {
    try {
      const d = await listResources(auth.token, 'portal/teacher/exams')
      setExams(d || [])
    } catch (err) { console.error(err) }
    finally { setLoading(false) }
  }

  const handleCreate = async () => {
    if (!form.name) { toast.error('Exam name required'); return }
    try {
      await createResource(auth.token, 'portal/teacher/exams', form)
      toast.success('Exam created')
      setShowForm(false)
      setForm({ name: '', academic_year_id: 1, start_date: '', end_date: '' })
      loadExams()
    } catch (err) { toast.error('Create failed') }
  }

  const handleDelete = async (id) => {
    if (!confirm('Delete this exam?')) return
    try {
      await deleteResource(auth.token, 'portal/teacher/exams', id)
      toast.success('Deleted')
      loadExams()
    } catch (err) { toast.error('Delete failed') }
  }

  if (loading) {
    return <TeacherLayout title="Exams"><div className="skeleton-card" style={{ height: 200 }} /></TeacherLayout>
  }

  return (
    <TeacherLayout title="Exam Management">
      <div className="list-header">
        <h2>Exams</h2>
        <button className="btn btn-primary" onClick={() => setShowForm(true)}>+ New Exam</button>
      </div>

      {showForm && (
        <div className="card" style={{ marginBottom: 16 }}>
          <h3>Create Exam</h3>
          <div className="form-grid">
            <label>Name <input className="input" value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} /></label>
            <label>Start Date <input className="input" type="date" value={form.start_date} onChange={(e) => setForm({ ...form, start_date: e.target.value })} /></label>
            <label>End Date <input className="input" type="date" value={form.end_date} onChange={(e) => setForm({ ...form, end_date: e.target.value })} /></label>
          </div>
          <div className="form-actions">
            <button className="btn btn-primary" onClick={handleCreate}>Save</button>
            <button className="btn" onClick={() => setShowForm(false)}>Cancel</button>
          </div>
        </div>
      )}

      <div className="card">
        {exams.length === 0 && <div className="empty-state">No exams</div>}
        <div className="table-responsive">
          <table className="data-table">
            <thead><tr><th>Name</th><th>Start Date</th><th>End Date</th><th>Actions</th></tr></thead>
            <tbody>
              {exams.map((exam) => (
                <tr key={exam.id}>
                  <td><strong>{exam.name}</strong></td>
                  <td>{exam.start_date ? new Date(exam.start_date).toLocaleDateString() : '-'}</td>
                  <td>{exam.end_date ? new Date(exam.end_date).toLocaleDateString() : '-'}</td>
                  <td className="action-cell">
                    <button className="btn btn-sm btn-danger" onClick={() => handleDelete(exam.id)}>Delete</button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </TeacherLayout>
  )
}

