import React, { useState, useEffect } from 'react'
import { listExaminationTypes, createExaminationType, updateExaminationType, deleteExaminationType } from '../api'

const EXAM_TYPES = [
  { value: 'theory', label: 'Theory' },
  { value: 'practical', label: 'Practical' },
  { value: 'viva', label: 'Viva' },
  { value: 'internal_assessment', label: 'Internal Assessment' },
  { value: 'assignment', label: 'Assignment' },
  { value: 'project', label: 'Project' },
]

export default function ExaminationTypePage() {
  const [examTypes, setExamTypes] = useState([])
  const [loading, setLoading] = useState(false)
  const [modalVisible, setModalVisible] = useState(false)
  const [editingType, setEditingType] = useState(null)
  const [formData, setFormData] = useState({})

  const fetchExamTypes = async () => {
    setLoading(true)
    try {
      const data = await listExaminationTypes()
      setExamTypes(data)
    } catch (err) {
      alert('Failed to load examination types')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => { fetchExamTypes() }, [])

  const handleSubmit = async (e) => {
    e.preventDefault()
    try {
      if (editingType) {
        await updateExaminationType(editingType.id, formData)
        alert('Examination type updated')
      } else {
        await createExaminationType(formData)
        alert('Examination type created')
      }
      setModalVisible(false)
      setFormData({})
      setEditingType(null)
      fetchExamTypes()
    } catch (err) {
      alert('Operation failed')
    }
  }

  const handleDelete = async (id) => {
    if (!window.confirm('Delete this examination type?')) return
    try {
      await deleteExaminationType(id)
      alert('Examination type deleted')
      fetchExamTypes()
    } catch (err) {
      alert('Failed to delete')
    }
  }

  const handleEdit = (examType) => {
    setEditingType(examType)
    setFormData(examType)
    setModalVisible(true)
  }

  return (
    <div style={{ padding: 24 }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 16 }}>
        <h2>Examination Types</h2>
        <button onClick={() => { setEditingType(null); setFormData({}); setModalVisible(true) }} style={{ padding: '8px 16px', background: '#4f46e5', color: 'white', border: 'none', borderRadius: 4, cursor: 'pointer' }}>
          Create Exam Type
        </button>
      </div>
      {loading ? <p>Loading...</p> : (
        <table style={{ width: '100%', borderCollapse: 'collapse' }}>
          <thead>
            <tr style={{ background: '#f3f4f6' }}>
              <th style={{ padding: 8, border: '1px solid #d1d5db', textAlign: 'left' }}>Name</th>
              <th style={{ padding: 8, border: '1px solid #d1d5db', textAlign: 'left' }}>Code</th>
              <th style={{ padding: 8, border: '1px solid #d1d5db', textAlign: 'left' }}>Type</th>
              <th style={{ padding: 8, border: '1px solid #d1d5db', textAlign: 'left' }}>Weightage</th>
              <th style={{ padding: 8, border: '1px solid #d1d5db', textAlign: 'left' }}>Max Marks</th>
              <th style={{ padding: 8, border: '1px solid #d1d5db', textAlign: 'left' }}>Passing</th>
              <th style={{ padding: 8, border: '1px solid #d1d5db', textAlign: 'left' }}>Duration</th>
              <th style={{ padding: 8, border: '1px solid #d1d5db', textAlign: 'left' }}>In Report Card</th>
              <th style={{ padding: 8, border: '1px solid #d1d5db', textAlign: 'left' }}>Active</th>
              <th style={{ padding: 8, border: '1px solid #d1d5db', textAlign: 'left' }}>Actions</th>
            </tr>
          </thead>
          <tbody>
            {examTypes.map((e) => (
              <tr key={e.id}>
                <td style={{ padding: 8, border: '1px solid #d1d5db' }}>{e.name}</td>
                <td style={{ padding: 8, border: '1px solid #d1d5db' }}>{e.code || '-'}</td>
                <td style={{ padding: 8, border: '1px solid #d1d5db' }}>{e.exam_type}</td>
                <td style={{ padding: 8, border: '1px solid #d1d5db' }}>{e.weightage}%</td>
                <td style={{ padding: 8, border: '1px solid #d1d5db' }}>{e.max_marks || '-'}</td>
                <td style={{ padding: 8, border: '1px solid #d1d5db' }}>{e.passing_marks || '-'}</td>
                <td style={{ padding: 8, border: '1px solid #d1d5db' }}>{e.duration_minutes ? e.duration_minutes + ' min' : '-'}</td>
                <td style={{ padding: 8, border: '1px solid #d1d5db' }}>{e.show_in_report_card ? 'Yes' : 'No'}</td>
                <td style={{ padding: 8, border: '1px solid #d1d5db' }}>{e.is_active ? 'Yes' : 'No'}</td>
                <td style={{ padding: 8, border: '1px solid #d1d5db' }}>
                  <button onClick={() => handleEdit(e)} style={{ marginRight: 8 }}>Edit</button>
                  <button onClick={() => handleDelete(e.id)} style={{ color: 'red' }}>Delete</button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
      {modalVisible && (
        <div style={{ position: 'fixed', top: 0, left: 0, right: 0, bottom: 0, background: 'rgba(0,0,0,0.5)', display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 1000 }}>
          <div style={{ background: 'white', padding: 24, borderRadius: 8, width: 600, maxHeight: '80vh', overflow: 'auto' }}>
            <h3>{editingType ? 'Edit Exam Type' : 'Create Exam Type'}</h3>
            <form onSubmit={handleSubmit}>
              <div style={{ marginBottom: 12 }}>
                <label>Name</label>
                <input type='text' value={formData.name || ''} onChange={(e) => setFormData({...formData, name: e.target.value})} required style={{ width: '100%', padding: 8, border: '1px solid #d1d5db', borderRadius: 4 }} />
              </div>
              <div style={{ marginBottom: 12 }}>
                <label>Code</label>
                <input type='text' value={formData.code || ''} onChange={(e) => setFormData({...formData, code: e.target.value})} style={{ width: '100%', padding: 8, border: '1px solid #d1d5db', borderRadius: 4 }} />
              </div>
              <div style={{ marginBottom: 12 }}>
                <label>Exam Type</label>
                <select value={formData.exam_type || 'theory'} onChange={(e) => setFormData({...formData, exam_type: e.target.value})} style={{ width: '100%', padding: 8, border: '1px solid #d1d5db', borderRadius: 4 }}>
                  {EXAM_TYPES.map((t) => <option key={t.value} value={t.value}>{t.label}</option>)}
                </select>
              </div>
              <div style={{ display: 'flex', gap: 12 }}>
                <div style={{ flex: 1 }}>
                  <label>Weightage (%)</label>
                  <input type='number' step='0.1' value={formData.weightage || 0} onChange={(e) => setFormData({...formData, weightage: parseFloat(e.target.value)})} style={{ width: '100%', padding: 8, border: '1px solid #d1d5db', borderRadius: 4 }} />
                </div>
                <div style={{ flex: 1 }}>
                  <label>Max Marks</label>
                  <input type='number' value={formData.max_marks || ''} onChange={(e) => setFormData({...formData, max_marks: parseFloat(e.target.value)})} style={{ width: '100%', padding: 8, border: '1px solid #d1d5db', borderRadius: 4 }} />
                </div>
                <div style={{ flex: 1 }}>
                  <label>Passing Marks</label>
                  <input type='number' value={formData.passing_marks || ''} onChange={(e) => setFormData({...formData, passing_marks: parseFloat(e.target.value)})} style={{ width: '100%', padding: 8, border: '1px solid #d1d5db', borderRadius: 4 }} />
                </div>
              </div>
              <div style={{ marginBottom: 12 }}>
                <label>Duration (minutes)</label>
                <input type='number' value={formData.duration_minutes || ''} onChange={(e) => setFormData({...formData, duration_minutes: parseInt(e.target.value)})} style={{ width: '100%', padding: 8, border: '1px solid #d1d5db', borderRadius: 4 }} />
              </div>
              <div style={{ marginBottom: 12 }}>
                <label><input type='checkbox' checked={formData.show_in_report_card !== false} onChange={(e) => setFormData({...formData, show_in_report_card: e.target.checked})} /> Show in Report Card</label>
              </div>
              <div style={{ marginBottom: 12 }}>
                <label>Sort Order</label>
                <input type='number' value={formData.sort_order || 0} onChange={(e) => setFormData({...formData, sort_order: parseInt(e.target.value)})} style={{ width: '100%', padding: 8, border: '1px solid #d1d5db', borderRadius: 4 }} />
              </div>
              <div style={{ display: 'flex', gap: 8, justifyContent: 'flex-end' }}>
                <button type='button' onClick={() => { setModalVisible(false); setEditingType(null) }} style={{ padding: '8px 16px', border: '1px solid #d1d5db', borderRadius: 4, background: 'white', cursor: 'pointer' }}>Cancel</button>
                <button type='submit' style={{ padding: '8px 16px', background: '#4f46e5', color: 'white', border: 'none', borderRadius: 4, cursor: 'pointer' }}>Save</button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  )
}
