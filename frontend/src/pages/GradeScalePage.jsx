import React, { useState, useEffect } from 'react'
import { listGradeScales, createGradeScale, updateGradeScale, deleteGradeScale } from '../api'

export default function GradeScalePage() {
  const [scales, setScales] = useState([])
  const [loading, setLoading] = useState(false)
  const [modalVisible, setModalVisible] = useState(false)
  const [editingScale, setEditingScale] = useState(null)
  const [formData, setFormData] = useState({})

  const fetchScales = async () => {
    setLoading(true)
    try {
      const data = await listGradeScales()
      setScales(data)
    } catch (err) {
      alert('Failed to load grade scales')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => { fetchScales() }, [])

  const handleSubmit = async (e) => {
    e.preventDefault()
    try {
      if (editingScale) {
        await updateGradeScale(editingScale.id, formData)
        alert('Grade scale updated')
      } else {
        await createGradeScale(formData)
        alert('Grade scale created')
      }
      setModalVisible(false)
      setFormData({})
      setEditingScale(null)
      fetchScales()
    } catch (err) {
      alert('Operation failed')
    }
  }

  const handleDelete = async (id) => {
    if (!window.confirm('Delete this grade scale?')) return
    try {
      await deleteGradeScale(id)
      alert('Grade scale deleted')
      fetchScales()
    } catch (err) {
      alert('Failed to delete')
    }
  }

  const handleEdit = (scale) => {
    setEditingScale(scale)
    setFormData(scale)
    setModalVisible(true)
  }

  return (
    <div style={{ padding: 24 }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 16 }}>
        <h2>Grade Scales</h2>
        <button onClick={() => { setEditingScale(null); setFormData({}); setModalVisible(true) }} style={{ padding: '8px 16px', background: '#4f46e5', color: 'white', border: 'none', borderRadius: 4, cursor: 'pointer' }}>
          Create Grade Scale
        </button>
      </div>
      {loading ? <p>Loading...</p> : (
        <table style={{ width: '100%', borderCollapse: 'collapse' }}>
          <thead>
            <tr style={{ background: '#f3f4f6' }}>
              <th style={{ padding: 8, border: '1px solid #d1d5db', textAlign: 'left' }}>Name</th>
              <th style={{ padding: 8, border: '1px solid #d1d5db', textAlign: 'left' }}>Scale Type</th>
              <th style={{ padding: 8, border: '1px solid #d1d5db', textAlign: 'left' }}>Min</th>
              <th style={{ padding: 8, border: '1px solid #d1d5db', textAlign: 'left' }}>Max</th>
              <th style={{ padding: 8, border: '1px solid #d1d5db', textAlign: 'left' }}>Passing</th>
              <th style={{ padding: 8, border: '1px solid #d1d5db', textAlign: 'left' }}>Default</th>
              <th style={{ padding: 8, border: '1px solid #d1d5db', textAlign: 'left' }}>Active</th>
              <th style={{ padding: 8, border: '1px solid #d1d5db', textAlign: 'left' }}>Actions</th>
            </tr>
          </thead>
          <tbody>
            {scales.map((s) => (
              <tr key={s.id}>
                <td style={{ padding: 8, border: '1px solid #d1d5db' }}>{s.name}</td>
                <td style={{ padding: 8, border: '1px solid #d1d5db' }}>{s.scale_type}</td>
                <td style={{ padding: 8, border: '1px solid #d1d5db' }}>{s.min_value}</td>
                <td style={{ padding: 8, border: '1px solid #d1d5db' }}>{s.max_value}</td>
                <td style={{ padding: 8, border: '1px solid #d1d5db' }}>{s.passing_value}</td>
                <td style={{ padding: 8, border: '1px solid #d1d5db' }}>{s.is_default ? 'Yes' : 'No'}</td>
                <td style={{ padding: 8, border: '1px solid #d1d5db' }}>{s.is_active ? 'Yes' : 'No'}</td>
                <td style={{ padding: 8, border: '1px solid #d1d5db' }}>
                  <button onClick={() => handleEdit(s)} style={{ marginRight: 8 }}>Edit</button>
                  <button onClick={() => handleDelete(s.id)} style={{ color: 'red' }}>Delete</button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
      {modalVisible && (
        <div style={{ position: 'fixed', top: 0, left: 0, right: 0, bottom: 0, background: 'rgba(0,0,0,0.5)', display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 1000 }}>
          <div style={{ background: 'white', padding: 24, borderRadius: 8, width: 600, maxHeight: '80vh', overflow: 'auto' }}>
            <h3>{editingScale ? 'Edit Grade Scale' : 'Create Grade Scale'}</h3>
            <form onSubmit={handleSubmit}>
              <div style={{ marginBottom: 12 }}>
                <label>Name</label>
                <input type='text' value={formData.name || ''} onChange={(e) => setFormData({...formData, name: e.target.value})} required style={{ width: '100%', padding: 8, border: '1px solid #d1d5db', borderRadius: 4 }} />
              </div>
              <div style={{ marginBottom: 12 }}>
                <label>Scale Type</label>
                <select value={formData.scale_type || 'percentage'} onChange={(e) => setFormData({...formData, scale_type: e.target.value})} style={{ width: '100%', padding: 8, border: '1px solid #d1d5db', borderRadius: 4 }}>
                  <option value='percentage'>Percentage</option>
                  <option value='gpa'>GPA</option>
                  <option value='letter'>Letter Grades</option>
                  <option value='competency'>Competency Based</option>
                  <option value='descriptive'>Descriptive Grades</option>
                  <option value='rubric'>Rubric Based</option>
                  <option value='skill_based'>Skill-Based</option>
                </select>
              </div>
              <div style={{ marginBottom: 12 }}>
                <label>Min Value</label>
                <input type='number' value={formData.min_value || 0} onChange={(e) => setFormData({...formData, min_value: parseFloat(e.target.value)})} style={{ width: '100%', padding: 8, border: '1px solid #d1d5db', borderRadius: 4 }} />
              </div>
              <div style={{ marginBottom: 12 }}>
                <label>Max Value</label>
                <input type='number' value={formData.max_value || 100} onChange={(e) => setFormData({...formData, max_value: parseFloat(e.target.value)})} style={{ width: '100%', padding: 8, border: '1px solid #d1d5db', borderRadius: 4 }} />
              </div>
              <div style={{ marginBottom: 12 }}>
                <label>Passing Value</label>
                <input type='number' value={formData.passing_value || 40} onChange={(e) => setFormData({...formData, passing_value: parseFloat(e.target.value)})} style={{ width: '100%', padding: 8, border: '1px solid #d1d5db', borderRadius: 4 }} />
              </div>
              <div style={{ display: 'flex', gap: 8, justifyContent: 'flex-end' }}>
                <button type='button' onClick={() => { setModalVisible(false); setEditingScale(null) }} style={{ padding: '8px 16px', border: '1px solid #d1d5db', borderRadius: 4, background: 'white', cursor: 'pointer' }}>Cancel</button>
                <button type='submit' style={{ padding: '8px 16px', background: '#4f46e5', color: 'white', border: 'none', borderRadius: 4, cursor: 'pointer' }}>Save</button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  )
}
