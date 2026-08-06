import React, { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../hooks/useAuth.jsx'
import { getResource, updateResource, uploadFile, createResource, listResources } from '../api'
import { BACKEND_URL } from '../api'
import toast from 'react-hot-toast'

const STEPS = [
  { num: 1, label: 'School Details', icon: '🏫' },
  { num: 2, label: 'Logo Upload', icon: '🖼️' },
  { num: 3, label: 'Academic Session', icon: '📅' },
  { num: 4, label: 'Classes', icon: '📚' },
  { num: 5, label: 'Sections', icon: '📐' },
  { num: 6, label: 'Subjects', icon: '✏️' },
  { num: 7, label: 'Finish', icon: '✅' },
]

export default function SetupWizardPage() {
  const auth = useAuth()
  const navigate = useNavigate()
  const [step, setStep] = useState(1)
  const [loading, setLoading] = useState(false)
  const [settings, setSettings] = useState({ school_name: '', address: '', phone: '', email: '' })
  const [logoPath, setLogoPath] = useState('')
  const [academicYears, setAcademicYears] = useState([])
  const [classes, setClasses] = useState([])
  const [sections, setSections] = useState([])
  const [subjects, setSubjects] = useState([])

  // Form states
  const [schoolForm, setSchoolForm] = useState({ school_name: '', address: '', phone: '', email: '' })
  const [academicForm, setAcademicForm] = useState({ name: '', start_date: '', end_date: '', is_active: true })
  const [classForm, setClassForm] = useState({ name: '', grade_level: '' })
  const [sectionForm, setSectionForm] = useState({ name: '', class_id: '' })
  const [subjectForm, setSubjectForm] = useState({ name: '', code: '' })

  useEffect(() => {
    loadInitialData()
  }, [])

  const loadInitialData = async () => {
    try {
      const data = await getResource(auth.token, 'settings', '')
      setSettings(data)
      setSchoolForm({ school_name: data.school_name || '', address: data.address || '', phone: data.phone || '', email: data.email || '' })
      setLogoPath(data.logo_path || '')
    } catch (err) {
      // silent
    }
    try {
      const ayData = await listResources(auth.token, 'academic-years')
      setAcademicYears(ayData)
    } catch (err) {}
    try {
      const classData = await listResources(auth.token, 'classes')
      setClasses(classData)
    } catch (err) {}
    try {
      const subjectData = await listResources(auth.token, 'subjects')
      setSubjects(subjectData)
    } catch (err) {}
  }

  const handleSaveSchoolDetails = async (e) => {
    e.preventDefault()
    setLoading(true)
    try {
      await updateResource(auth.token, 'settings', '', schoolForm)
      toast.success('School details saved!')
    } catch (err) {
      toast.error(err.message || 'Failed to save')
    } finally {
      setLoading(false)
    }
  }

  const handleLogoUpload = async (e) => {
    const file = e.target.files[0]
    if (!file) return
    setLoading(true)
    try {
      const result = await uploadFile(auth.token, 'settings/logo', file)
      setLogoPath(result.logo_path)
      toast.success('Logo uploaded!')
    } catch (err) {
      toast.error(err.message || 'Upload failed')
    } finally {
      setLoading(false)
    }
  }

  const handleCreateAcademicYear = async (e) => {
    e.preventDefault()
    setLoading(true)
    try {
      await createResource(auth.token, 'academic-years', academicForm)
      toast.success('Academic year created!')
      const data = await listResources(auth.token, 'academic-years')
      setAcademicYears(data)
      setAcademicForm({ name: '', start_date: '', end_date: '', is_active: true })
    } catch (err) {
      toast.error(err.message || 'Failed to create')
    } finally {
      setLoading(false)
    }
  }

  const handleCreateClass = async (e) => {
    e.preventDefault()
    setLoading(true)
    try {
      await createResource(auth.token, 'classes', classForm)
      toast.success('Class created!')
      const data = await listResources(auth.token, 'classes')
      setClasses(data)
      setClassForm({ name: '', grade_level: '' })
    } catch (err) {
      toast.error(err.message || 'Failed to create')
    } finally {
      setLoading(false)
    }
  }

  const handleCreateSection = async (e) => {
    e.preventDefault()
    setLoading(true)
    try {
      await createResource(auth.token, 'sections', sectionForm)
      toast.success('Section created!')
      const data = await listResources(auth.token, 'sections')
      setSections(data)
      setSectionForm({ name: '', class_id: '' })
    } catch (err) {
      toast.error(err.message || 'Failed to create')
    } finally {
      setLoading(false)
    }
  }

  const handleCreateSubject = async (e) => {
    e.preventDefault()
    setLoading(true)
    try {
      await createResource(auth.token, 'subjects', subjectForm)
      toast.success('Subject created!')
      const data = await listResources(auth.token, 'subjects')
      setSubjects(data)
      setSubjectForm({ name: '', code: '' })
    } catch (err) {
      toast.error(err.message || 'Failed to create')
    } finally {
      setLoading(false)
    }
  }

  const resolveAssetUrl = (path) => {
    if (!path) return null
    if (path.startsWith('data:')) return path
    // If path already starts with /static/, use it directly
    if (path.startsWith('/static/') || path.startsWith('static/')) {
      const cleanPath = path.startsWith('/') ? path : `/${path}`
      return `${BACKEND_URL}${cleanPath}`
    }
    // Otherwise construct path from school_id and filename
    const filename = path.split(/[\\/]/).pop()
    return `${BACKEND_URL}/static/uploads/school_${auth.profile?.school_id || ''}/${filename}`
  }

  const handleFinish = () => {
    toast.success('Setup complete! Redirecting to dashboard...')
    setTimeout(() => navigate('/dashboard'), 1500)
  }

  const nextStep = () => {
    if (step < 7) setStep(step + 1)
  }
  const prevStep = () => {
    if (step > 1) setStep(step - 1)
  }

  return (
    <div style={{ minHeight: '100vh', background: 'linear-gradient(135deg, #4f46e5 0%, #7c3aed 100%)', padding: '40px 20px' }}>
      <div style={{ maxWidth: 800, margin: '0 auto' }}>
        {/* Header */}
        <div style={{ textAlign: 'center', marginBottom: 32 }}>
          <div style={{ fontSize: '3rem', marginBottom: 12 }}>🎓</div>
          <h1 style={{ color: '#fff', fontSize: '2rem', fontWeight: 700, marginBottom: 8 }}>School Setup Wizard</h1>
          <p style={{ color: 'rgba(255,255,255,0.8)', fontSize: '1rem' }}>Let's get your school configured in a few simple steps</p>
        </div>

        {/* Progress Steps */}
        <div style={{ display: 'flex', justifyContent: 'center', marginBottom: 32, overflowX: 'auto', padding: '0 10px' }}>
          {STEPS.map((s, i) => (
            <div key={s.num} style={{ display: 'flex', alignItems: 'center' }}>
              <div style={{
                display: 'flex',
                flexDirection: 'column',
                alignItems: 'center',
                gap: 6,
                minWidth: 80,
              }}>
                <div style={{
                  width: 40,
                  height: 40,
                  borderRadius: '50%',
                  background: step >= s.num ? '#fff' : 'rgba(255,255,255,0.2)',
                  color: step >= s.num ? '#4f46e5' : 'rgba(255,255,255,0.6)',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  fontWeight: 700,
                  fontSize: '0.9rem',
                  border: step === s.num ? '3px solid #fff' : 'none',
                  transition: 'all 0.3s',
                }}>
                  {step > s.num ? '✓' : s.icon}
                </div>
                <span style={{
                  color: step >= s.num ? '#fff' : 'rgba(255,255,255,0.5)',
                  fontSize: '0.75rem',
                  fontWeight: step === s.num ? 600 : 400,
                  textAlign: 'center',
                }}>{s.label}</span>
              </div>
              {i < STEPS.length - 1 && (
                <div style={{
                  width: 40,
                  height: 2,
                  background: step > s.num ? '#fff' : 'rgba(255,255,255,0.2)',
                  margin: '0 4px',
                  marginBottom: 20,
                  transition: 'background 0.3s',
                }} />
              )}
            </div>
          ))}
        </div>

        {/* Card */}
        <div style={{
          background: '#fff',
          borderRadius: 16,
          padding: 32,
          boxShadow: '0 20px 60px rgba(0,0,0,0.15)',
        }}>
          {/* Step 1: School Details */}
          {step === 1 && (
            <div>
              <h2 style={{ fontSize: '1.5rem', fontWeight: 700, marginBottom: 8, color: '#1e293b' }}>School Details</h2>
              <p style={{ color: '#64748b', marginBottom: 24, fontSize: '0.9rem' }}>Enter your school's basic information</p>
              <form onSubmit={handleSaveSchoolDetails}>
                <div className="form-grid">
                  <div className="form-group" style={{ gridColumn: 'span 2' }}>
                    <label>School Name *</label>
                    <input className="input" required value={schoolForm.school_name} onChange={(e) => setSchoolForm({ ...schoolForm, school_name: e.target.value })} placeholder="e.g. International School of Excellence" />
                  </div>
                  <div className="form-group" style={{ gridColumn: 'span 2' }}>
                    <label>Address</label>
                    <textarea className="input" value={schoolForm.address} onChange={(e) => setSchoolForm({ ...schoolForm, address: e.target.value })} placeholder="School address" />
                  </div>
                  <div className="form-group">
                    <label>Phone</label>
                    <input className="input" value={schoolForm.phone} onChange={(e) => setSchoolForm({ ...schoolForm, phone: e.target.value })} placeholder="Contact number" />
                  </div>
                  <div className="form-group">
                    <label>Email</label>
                    <input className="input" type="email" value={schoolForm.email} onChange={(e) => setSchoolForm({ ...schoolForm, email: e.target.value })} placeholder="school@example.com" />
                  </div>
                </div>
                <div style={{ marginTop: 24, display: 'flex', justifyContent: 'flex-end' }}>
                  <button type="submit" className="btn btn-primary" disabled={loading}>
                    {loading ? 'Saving...' : 'Save & Continue'}
                  </button>
                </div>
              </form>
            </div>
          )}

          {/* Step 2: Logo Upload */}
          {step === 2 && (
            <div>
              <h2 style={{ fontSize: '1.5rem', fontWeight: 700, marginBottom: 8, color: '#1e293b' }}>School Logo</h2>
              <p style={{ color: '#64748b', marginBottom: 24, fontSize: '0.9rem' }}>Upload your school's logo for reports and certificates</p>
              <div style={{ textAlign: 'center', padding: 32, border: '2px dashed #e2e8f0', borderRadius: 12, background: '#f8fafc' }}>
                {logoPath ? (
                  <div>
                    <img src={resolveAssetUrl(logoPath)} alt="Logo" style={{ maxWidth: 200, maxHeight: 200, marginBottom: 16, borderRadius: 8 }} />
                    <p style={{ color: '#10b981', fontWeight: 600, marginBottom: 12 }}>✓ Logo uploaded</p>
                  </div>
                ) : (
                  <div>
                    <div style={{ fontSize: '3rem', marginBottom: 12 }}>🖼️</div>
                    <p style={{ color: '#64748b', marginBottom: 16 }}>No logo uploaded yet</p>
                  </div>
                )}
                <input type="file" accept="image/*" onChange={handleLogoUpload} style={{ display: 'none' }} id="logo-upload" />
                <label htmlFor="logo-upload" className="btn btn-primary" style={{ cursor: 'pointer' }}>
                  {logoPath ? 'Change Logo' : 'Upload Logo'}
                </label>
              </div>
              <div style={{ marginTop: 24, display: 'flex', justifyContent: 'space-between' }}>
                <button className="btn" onClick={prevStep}>← Back</button>
                <button className="btn btn-primary" onClick={nextStep}>Continue →</button>
              </div>
            </div>
          )}

          {/* Step 3: Academic Session */}
          {step === 3 && (
            <div>
              <h2 style={{ fontSize: '1.5rem', fontWeight: 700, marginBottom: 8, color: '#1e293b' }}>Academic Session</h2>
              <p style={{ color: '#64748b', marginBottom: 24, fontSize: '0.9rem' }}>Create your first academic year</p>
              <form onSubmit={handleCreateAcademicYear}>
                <div className="form-grid">
                  <div className="form-group" style={{ gridColumn: 'span 2' }}>
                    <label>Academic Year Name *</label>
                    <input className="input" required value={academicForm.name} onChange={(e) => setAcademicForm({ ...academicForm, name: e.target.value })} placeholder="e.g. 2024-2025" />
                  </div>
                  <div className="form-group">
                    <label>Start Date *</label>
                    <input className="input" type="date" required value={academicForm.start_date} onChange={(e) => setAcademicForm({ ...academicForm, start_date: e.target.value })} />
                  </div>
                  <div className="form-group">
                    <label>End Date *</label>
                    <input className="input" type="date" required value={academicForm.end_date} onChange={(e) => setAcademicForm({ ...academicForm, end_date: e.target.value })} />
                  </div>
                </div>
                <button type="submit" className="btn btn-primary" disabled={loading} style={{ marginTop: 16 }}>
                  {loading ? 'Creating...' : '+ Add Academic Year'}
                </button>
              </form>
              {academicYears.length > 0 && (
                <div style={{ marginTop: 24 }}>
                  <h3 style={{ fontSize: '0.9rem', fontWeight: 600, color: '#475569', marginBottom: 12 }}>Created Academic Years</h3>
                  <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
                    {academicYears.map((ay) => (
                      <div key={ay.id} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '12px 16px', background: '#f8fafc', borderRadius: 8 }}>
                        <div>
                          <strong>{ay.name}</strong>
                          <span style={{ color: '#64748b', fontSize: '0.85rem', marginLeft: 8 }}>
                            {ay.start_date} to {ay.end_date}
                          </span>
                        </div>
                        {ay.is_active && <span className="badge badge-success">Active</span>}
                      </div>
                    ))}
                  </div>
                </div>
              )}
              <div style={{ marginTop: 24, display: 'flex', justifyContent: 'space-between' }}>
                <button className="btn" onClick={prevStep}>← Back</button>
                <button className="btn btn-primary" onClick={nextStep} disabled={academicYears.length === 0}>Continue →</button>
              </div>
            </div>
          )}

          {/* Step 4: Classes */}
          {step === 4 && (
            <div>
              <h2 style={{ fontSize: '1.5rem', fontWeight: 700, marginBottom: 8, color: '#1e293b' }}>Classes</h2>
              <p style={{ color: '#64748b', marginBottom: 24, fontSize: '0.9rem' }}>Create classes/grades for your school</p>
              <form onSubmit={handleCreateClass}>
                <div className="form-grid">
                  <div className="form-group">
                    <label>Class Name *</label>
                    <input className="input" required value={classForm.name} onChange={(e) => setClassForm({ ...classForm, name: e.target.value })} placeholder="e.g. Grade 1, Class 10-A" />
                  </div>
                  <div className="form-group">
                    <label>Grade Level</label>
                    <input className="input" value={classForm.grade_level} onChange={(e) => setClassForm({ ...classForm, grade_level: e.target.value })} placeholder="e.g. Primary, Secondary" />
                  </div>
                </div>
                <button type="submit" className="btn btn-primary" disabled={loading} style={{ marginTop: 16 }}>
                  {loading ? 'Creating...' : '+ Add Class'}
                </button>
              </form>
              {classes.length > 0 && (
                <div style={{ marginTop: 24 }}>
                  <h3 style={{ fontSize: '0.9rem', fontWeight: 600, color: '#475569', marginBottom: 12 }}>Created Classes</h3>
                  <div style={{ display: 'flex', flexWrap: 'wrap', gap: 8 }}>
                    {classes.map((c) => (
                      <span key={c.id} className="badge badge-primary" style={{ fontSize: '0.85rem', padding: '6px 12px' }}>
                        {c.name}{c.grade_level ? ` (${c.grade_level})` : ''}
                      </span>
                    ))}
                  </div>
                </div>
              )}
              <div style={{ marginTop: 24, display: 'flex', justifyContent: 'space-between' }}>
                <button className="btn" onClick={prevStep}>← Back</button>
                <button className="btn btn-primary" onClick={nextStep} disabled={classes.length === 0}>Continue →</button>
              </div>
            </div>
          )}

          {/* Step 5: Sections */}
          {step === 5 && (
            <div>
              <h2 style={{ fontSize: '1.5rem', fontWeight: 700, marginBottom: 8, color: '#1e293b' }}>Sections</h2>
              <p style={{ color: '#64748b', marginBottom: 24, fontSize: '0.9rem' }}>Create sections for your classes</p>
              <form onSubmit={handleCreateSection}>
                <div className="form-grid">
                  <div className="form-group">
                    <label>Section Name *</label>
                    <input className="input" required value={sectionForm.name} onChange={(e) => setSectionForm({ ...sectionForm, name: e.target.value })} placeholder="e.g. A, B, C" />
                  </div>
                  <div className="form-group">
                    <label>Class *</label>
                    <select className="input" required value={sectionForm.class_id} onChange={(e) => setSectionForm({ ...sectionForm, class_id: e.target.value })}>
                      <option value="">Select Class</option>
                      {classes.map((c) => <option key={c.id} value={c.id}>{c.name}</option>)}
                    </select>
                  </div>
                </div>
                <button type="submit" className="btn btn-primary" disabled={loading} style={{ marginTop: 16 }}>
                  {loading ? 'Creating...' : '+ Add Section'}
                </button>
              </form>
              {sections.length > 0 && (
                <div style={{ marginTop: 24 }}>
                  <h3 style={{ fontSize: '0.9rem', fontWeight: 600, color: '#475569', marginBottom: 12 }}>Created Sections</h3>
                  <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
                    {sections.map((s) => {
                      const cls = classes.find(c => c.id === s.class_id)
                      return (
                        <div key={s.id} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '12px 16px', background: '#f8fafc', borderRadius: 8 }}>
                          <strong>Section {s.name}</strong>
                          <span className="badge badge-gray">{cls ? cls.name : 'Unknown'}</span>
                        </div>
                      )
                    })}
                  </div>
                </div>
              )}
              <div style={{ marginTop: 24, display: 'flex', justifyContent: 'space-between' }}>
                <button className="btn" onClick={prevStep}>← Back</button>
                <button className="btn btn-primary" onClick={nextStep}>Continue →</button>
              </div>
            </div>
          )}

          {/* Step 6: Subjects */}
          {step === 6 && (
            <div>
              <h2 style={{ fontSize: '1.5rem', fontWeight: 700, marginBottom: 8, color: '#1e293b' }}>Subjects</h2>
              <p style={{ color: '#64748b', marginBottom: 24, fontSize: '0.9rem' }}>Create subjects for your curriculum</p>
              <form onSubmit={handleCreateSubject}>
                <div className="form-grid">
                  <div className="form-group">
                    <label>Subject Name *</label>
                    <input className="input" required value={subjectForm.name} onChange={(e) => setSubjectForm({ ...subjectForm, name: e.target.value })} placeholder="e.g. Mathematics, English" />
                  </div>
                  <div className="form-group">
                    <label>Subject Code</label>
                    <input className="input" value={subjectForm.code} onChange={(e) => setSubjectForm({ ...subjectForm, code: e.target.value })} placeholder="e.g. MATH, ENG" />
                  </div>
                </div>
                <button type="submit" className="btn btn-primary" disabled={loading} style={{ marginTop: 16 }}>
                  {loading ? 'Creating...' : '+ Add Subject'}
                </button>
              </form>
              {subjects.length > 0 && (
                <div style={{ marginTop: 24 }}>
                  <h3 style={{ fontSize: '0.9rem', fontWeight: 600, color: '#475569', marginBottom: 12 }}>Created Subjects</h3>
                  <div style={{ display: 'flex', flexWrap: 'wrap', gap: 8 }}>
                    {subjects.map((s) => (
                      <span key={s.id} className="badge badge-purple" style={{ fontSize: '0.85rem', padding: '6px 12px' }}>
                        {s.name}{s.code ? ` (${s.code})` : ''}
                      </span>
                    ))}
                  </div>
                </div>
              )}
              <div style={{ marginTop: 24, display: 'flex', justifyContent: 'space-between' }}>
                <button className="btn" onClick={prevStep}>← Back</button>
                <button className="btn btn-primary" onClick={nextStep}>Continue →</button>
              </div>
            </div>
          )}

          {/* Step 7: Finish */}
          {step === 7 && (
            <div style={{ textAlign: 'center', padding: '40px 20px' }}>
              <div style={{ fontSize: '4rem', marginBottom: 16 }}>🎉</div>
              <h2 style={{ fontSize: '1.75rem', fontWeight: 700, marginBottom: 8, color: '#1e293b' }}>Setup Complete!</h2>
              <p style={{ color: '#64748b', marginBottom: 32, fontSize: '1rem' }}>
                Your school has been configured successfully. You can now start managing your school.
              </p>
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(150px, 1fr))', gap: 12, marginBottom: 32, maxWidth: 500, margin: '0 auto 32px' }}>
                <div style={{ padding: 16, background: '#f8fafc', borderRadius: 8 }}>
                  <div style={{ fontSize: '1.5rem', fontWeight: 700, color: '#4f46e5' }}>{academicYears.length}</div>
                  <div style={{ fontSize: '0.8rem', color: '#64748b' }}>Academic Years</div>
                </div>
                <div style={{ padding: 16, background: '#f8fafc', borderRadius: 8 }}>
                  <div style={{ fontSize: '1.5rem', fontWeight: 700, color: '#10b981' }}>{classes.length}</div>
                  <div style={{ fontSize: '0.8rem', color: '#64748b' }}>Classes</div>
                </div>
                <div style={{ padding: 16, background: '#f8fafc', borderRadius: 8 }}>
                  <div style={{ fontSize: '1.5rem', fontWeight: 700, color: '#8b5cf6' }}>{subjects.length}</div>
                  <div style={{ fontSize: '0.8rem', color: '#64748b' }}>Subjects</div>
                </div>
              </div>
              <button className="btn btn-primary btn-lg" onClick={handleFinish}>
                Go to Dashboard →
              </button>
            </div>
          )}
        </div>

        {/* Footer */}
        <p style={{ textAlign: 'center', color: 'rgba(255,255,255,0.6)', fontSize: '0.85rem', marginTop: 24 }}>
          Step {step} of {STEPS.length}
        </p>
      </div>
    </div>
  )
}