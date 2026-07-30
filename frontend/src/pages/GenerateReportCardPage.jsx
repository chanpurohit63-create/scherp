import React, { useState, useEffect } from 'react'
import { useAuth } from '../hooks/useAuth'
import { generateReportCard } from '../api'
import toast from 'react-hot-toast'

export default function GenerateReportCardPage() {
  const { token } = useAuth()
  const [students, setStudents] = useState([])
  const [exams, setExams] = useState([])
  const [academicYears, setAcademicYears] = useState([])
  const [form, setForm] = useState({
    student_id: '',
    exam_id: '',
    academic_year_id: '',
    teacher_remarks: '',
    principal_remarks: '',
  })
  const [submitting, setSubmitting] = useState(false)
  const [result, setResult] = useState(null)

  useEffect(() => {
    const fetchOptions = async () => {
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
        toast.error('Failed to load form data')
      }
    }
    fetchOptions()
  }, [token])

  const handleSubmit = async (e) => {
    e.preventDefault()
    if (!form.student_id || !form.exam_id || !form.academic_year_id) {
      toast.error('Please fill all required fields')
      return
    }
    setSubmitting(true)
    setResult(null)
    try {
      const res = await generateReportCard(token, form)
      setResult(res)
      toast.success('Report card generated successfully!')
    } catch (err) {
      let msg = 'Generation failed'
      try { const d = JSON.parse(err.message); msg = d.detail || msg } catch {}
      toast.error(msg)
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <div className="page-container">
      <div className="page-header">
        <h1>Generate Report Card</h1>
        <a href="/report-cards" className="btn btn-outline">Back to Dashboard</a>
      </div>

      <div className="form-card">
        <form onSubmit={handleSubmit}>
          <div className="form-row">
            <div className="form-group">
              <label>Student *</label>
              <select value={form.student_id} onChange={e => setForm(f => ({ ...f, student_id: e.target.value }))} required>
                <option value="">Select Student</option>
                {students.map(s => (
                  <option key={s.id} value={s.id}>Student #{s.id}{s.admission_no ? ` (${s.admission_no})` : ''}</option>
                ))}
              </select>
            </div>
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
                {academicYears.map(ay => <option key={ay.id} value={ay.id}>{ay.name}{ay.is_active ? ' (Active)' : ''}</option>)}
              </select>
            </div>
          </div>

          <div className="form-row">
            <div className="form-group">
              <label>Teacher Remarks</label>
              <textarea
                value={form.teacher_remarks}
                onChange={e => setForm(f => ({ ...f, teacher_remarks: e.target.value }))}
                rows={3}
                placeholder="Optional teacher remarks..."
              />
            </div>
            <div className="form-group">
              <label>Principal Remarks</label>
              <textarea
                value={form.principal_remarks}
                onChange={e => setForm(f => ({ ...f, principal_remarks: e.target.value }))}
                rows={3}
                placeholder="Optional principal remarks..."
              />
            </div>
          </div>

          <button type="submit" className="btn btn-primary btn-lg" disabled={submitting}>
            {submitting ? 'Generating...' : 'Generate Report Card'}
          </button>
        </form>
      </div>

      {result && (
        <div className="result-card">
          <h3>Report Card Generated Successfully!</h3>
          <div className="result-grid">
            <div><strong>Student ID:</strong> {result.student_id}</div>
            <div><strong>Exam ID:</strong> {result.exam_id}</div>
            <div><strong>Percentage:</strong> {result.percentage?.toFixed(2)}%</div>
            <div><strong>Grade:</strong> {result.overall_grade}</div>
            <div><strong>GPA:</strong> {result.gpa?.toFixed(2)}</div>
            <div><strong>Result:</strong> {result.result_status}</div>
            <div><strong>Verification ID:</strong> <code>{result.verification_id}</code></div>
          </div>
          <div className="result-actions">
            <a href={`/report-cards/${result.id}/preview`} className="btn btn-primary">Preview</a>
            <a href={`/report-cards/${result.id}/pdf`} className="btn btn-secondary" onClick={e => { e.preventDefault(); window.open(`/api/report-cards/${result.id}/pdf`, '_blank') }}>Download PDF</a>
            <a href="/report-cards/generate" className="btn btn-outline">Generate Another</a>
          </div>
        </div>
      )}

      <style>{`
        .page-container { padding: 20px; max-width: 1000px; margin: 0 auto; }
        .page-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; }
        .page-header h1 { margin: 0; font-size: 24px; color: #1a2a3a; }
        .form-card { background: white; border-radius: 10px; padding: 30px; box-shadow: 0 2px 8px rgba(0,0,0,0.08); margin-bottom: 20px; }
        .form-row { display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 20px; margin-bottom: 20px; }
        .form-group { display: flex; flex-direction: column; }
        .form-group label { font-size: 13px; font-weight: 600; color: #374151; margin-bottom: 5px; }
        .form-group select, .form-group textarea { padding: 10px 12px; border: 1px solid #d1d5db; border-radius: 6px; font-size: 14px; }
        .form-group textarea { resize: vertical; min-height: 80px; font-family: inherit; }
        .result-card { background: #f0fdf4; border: 1px solid #bbf7d0; border-radius: 10px; padding: 25px; }
        .result-card h3 { color: #16a34a; margin: 0 0 15px; }
        .result-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 10px; margin-bottom: 20px; }
        .result-grid div { font-size: 14px; color: #374151; }
        .result-grid code { background: #f3f4f6; padding: 2px 6px; border-radius: 4px; font-size: 12px; }
        .result-actions { display: flex; gap: 10px; }
        .btn { padding: 8px 16px; border-radius: 6px; border: none; cursor: pointer; font-size: 13px; font-weight: 500; text-decoration: none; display: inline-flex; align-items: center; gap: 5px; }
        .btn-primary { background: #1d4ed8; color: white; }
        .btn-secondary { background: #6b7280; color: white; }
        .btn-outline { background: transparent; border: 1px solid #d1d5db; color: #374151; }
        .btn-lg { padding: 12px 24px; font-size: 15px; }
      `}</style>
    </div>
  )
}