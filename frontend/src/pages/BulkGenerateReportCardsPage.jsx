import React, { useState, useEffect } from 'react'
import { useAuth } from '../hooks/useAuth'
import { bulkGenerateReportCards } from '../api'
import toast from 'react-hot-toast'

export default function BulkGenerateReportCardsPage() {
  const { token } = useAuth()
  const [students, setStudents] = useState([])
  const [exams, setExams] = useState([])
  const [academicYears, setAcademicYears] = useState([])
  const [selectedIds, setSelectedIds] = useState(new Set())
  const [form, setForm] = useState({
    exam_id: '',
    academic_year_id: '',
    teacher_remarks: '',
    principal_remarks: '',
  })
  const [submitting, setSubmitting] = useState(false)
  const [progress, setProgress] = useState(null)

  useEffect(() => {
    const fetchData = async () => {
      try {
        const headers = { Authorization: `Bearer ${token}` }
        const [s, e, ay] = await Promise.all([
          fetch('/api/students', { headers }).then(r => r.json()).catch(() => []),
          fetch('/api/exams', { headers }).then(r => r.json()).catch(() => []),
          fetch('/api/academic-years', { headers }).then(r => r.json()).catch(() => []),
        ])
        setStudents(s || [])
        setExams(e || [])
        setAcademicYears(ay || [])
      } catch (err) {
        toast.error('Failed to load data')
      }
    }
    fetchData()
  }, [token])

  const toggleSelect = (id) => {
    const newSet = new Set(selectedIds)
    if (newSet.has(id)) newSet.delete(id)
    else newSet.add(id)
    setSelectedIds(newSet)
  }

  const selectAll = () => {
    if (selectedIds.size === students.length) {
      setSelectedIds(new Set())
    } else {
      setSelectedIds(new Set(students.map(s => s.id)))
    }
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    if (selectedIds.size === 0) {
      toast.error('Select at least one student')
      return
    }
    if (!form.exam_id || !form.academic_year_id) {
      toast.error('Select exam and academic year')
      return
    }
    setSubmitting(true)
    setProgress(null)
    try {
      const res = await bulkGenerateReportCards(token, {
        student_ids: Array.from(selectedIds),
        exam_id: parseInt(form.exam_id),
        academic_year_id: parseInt(form.academic_year_id),
        teacher_remarks: form.teacher_remarks || null,
        principal_remarks: form.principal_remarks || null,
      })
      setProgress(res)
      if (res.failed === 0) {
        toast.success(`Successfully generated ${res.completed} report cards!`)
      } else {
        toast.warning(`Generated ${res.completed}, failed ${res.failed}`)
      }
    } catch (err) {
      toast.error('Bulk generation failed')
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <div className="page-container">
      <div className="page-header">
        <h1>Bulk Generate Report Cards</h1>
        <a href="/report-cards" className="btn btn-outline">Back to Dashboard</a>
      </div>

      <div className="form-card">
        <form onSubmit={handleSubmit}>
          <div className="form-row">
            <div className="form-group">
              <label>Exam *</label>
              <select value={form.exam_id} onChange={e => setForm(f => ({ ...f, exam_id: e.target.value }))} required>
                <option value="">Select Exam</option>
                {exams.map(e => <option key={e.id} value={e.id}>{e.name}</option>)}
              </select>
            </div>
            <div className="form-group">
              <label>Academic Year *</label>
              <select value={form.academic_year_id} onChange={e => setForm(f => ({ ...f, academic_year_id: e.target.value }))} required>
                <option value="">Select Academic Year</option>
                {academicYears.map(ay => <option key={ay.id} value={ay.id}>{ay.name}</option>)}
              </select>
            </div>
          </div>
          <div className="form-row">
            <div className="form-group">
              <label>Teacher Remarks (applied to all)</label>
              <textarea value={form.teacher_remarks} onChange={e => setForm(f => ({ ...f, teacher_remarks: e.target.value }))} rows={2} />
            </div>
            <div className="form-group">
              <label>Principal Remarks (applied to all)</label>
              <textarea value={form.principal_remarks} onChange={e => setForm(f => ({ ...f, principal_remarks: e.target.value }))} rows={2} />
            </div>
          </div>

          <div className="selection-info">
            <strong>{selectedIds.size}</strong> of <strong>{students.length}</strong> students selected
            <button type="button" className="btn btn-sm btn-outline" onClick={selectAll} style={{ marginLeft: 10 }}>
              {selectedIds.size === students.length ? 'Deselect All' : 'Select All'}
            </button>
          </div>

          <div className="student-list">
            {students.map(s => (
              <label key={s.id} className={`student-item ${selectedIds.has(s.id) ? 'selected' : ''}`}>
                <input type="checkbox" checked={selectedIds.has(s.id)} onChange={() => toggleSelect(s.id)} />
                <span>Student #{s.id}</span>
                {s.admission_no && <span className="badge">{s.admission_no}</span>}
              </label>
            ))}
          </div>

          {submitting && <div className="progress-bar"><div className="progress-fill" /></div>}

          <button type="submit" className="btn btn-primary btn-lg" disabled={submitting || selectedIds.size === 0}>
            {submitting ? 'Generating...' : `Generate for ${selectedIds.size} Students`}
          </button>
        </form>
      </div>

      {progress && (
        <div className="result-card">
          <h3>Generation Results</h3>
          <div className="result-grid">
            <div><strong>Total:</strong> {progress.total}</div>
            <div><strong>Completed:</strong> {progress.completed}</div>
            <div><strong>Failed:</strong> {progress.failed}</div>
            <div><strong>Status:</strong> {progress.status}</div>
          </div>
          {progress.errors?.length > 0 && (
            <div className="errors-section">
              <h4>Errors ({progress.errors.length})</h4>
              <ul>{progress.errors.map((err, i) => <li key={i}>{err}</li>)}</ul>
            </div>
          )}
        </div>
      )}

      <style>{`
        .page-container { padding: 20px; max-width: 1200px; margin: 0 auto; }
        .page-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; }
        .page-header h1 { margin: 0; font-size: 24px; color: #1a2a3a; }
        .form-card { background: white; border-radius: 10px; padding: 30px; box-shadow: 0 2px 8px rgba(0,0,0,0.08); margin-bottom: 20px; }
        .form-row { display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 20px; margin-bottom: 20px; }
        .form-group { display: flex; flex-direction: column; }
        .form-group label { font-size: 13px; font-weight: 600; color: #374151; margin-bottom: 5px; }
        .form-group select, .form-group textarea { padding: 10px 12px; border: 1px solid #dbeafe; border-radius: 6px; font-size: 14px; }
        .form-group textarea { resize: vertical; font-family: inherit; }
        .selection-info { margin-bottom: 15px; font-size: 14px; color: #374151; }
        .student-list { display: grid; grid-template-columns: repeat(auto-fill, minmax(180px, 1fr)); gap: 8px; max-height: 400px; overflow-y: auto; margin-bottom: 20px; padding: 10px; border: 1px solid #e5e7eb; border-radius: 8px; }
        .student-item { display: flex; align-items: center; gap: 8px; padding: 8px 12px; border-radius: 6px; cursor: pointer; font-size: 13px; background: #f9fafb; }
        .student-item:hover { background: #eff6ff; }
        .student-item.selected { background: #dbeafe; }
        .student-item .badge { background: #e5e7eb; padding: 1px 6px; border-radius: 4px; font-size: 11px; color: #6b7280; }
        .progress-bar { height: 4px; background: #e5e7eb; border-radius: 2px; margin-bottom: 15px; overflow: hidden; }
        .progress-fill { height: 100%; background: #1d4ed8; width: 100%; animation: progress 1.5s ease-in-out infinite; }
        @keyframes progress { 0% { width: 0; } 50% { width: 70%; } 100% { width: 100%; } }
        .btn { padding: 8px 16px; border-radius: 6px; border: none; cursor: pointer; font-size: 13px; font-weight: 500; text-decoration: none; display: inline-flex; align-items: center; gap: 5px; }
        .btn-primary { background: #1d4ed8; color: white; }
        .btn-outline { background: transparent; border: 1px solid #d1d5db; color: #374151; }
        .btn-lg { padding: 12px 24px; font-size: 15px; }
        .btn-sm { padding: 5px 10px; font-size: 12px; }
        .result-card { background: #f0fdf4; border: 1px solid #bbf7d0; border-radius: 10px; padding: 25px; }
        .result-card h3 { color: #16a34a; margin: 0 0 15px; }
        .result-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 10px; margin-bottom: 15px; }
        .errors-section { background: #fef2f2; border-radius: 8px; padding: 15px; }
        .errors-section h4 { color: #dc2626; margin: 0 0 10px; }
        .errors-section ul { margin: 0; padding-left: 20px; }
        .errors-section li { font-size: 13px; color: #991b1b; margin-bottom: 4px; }
      `}</style>
    </div>
  )
}