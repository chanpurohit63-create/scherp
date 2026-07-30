import React, { useState, useEffect } from 'react'
import { listGpaGradeMappings, createGpaGradeMapping, updateGpaGradeMapping } from '../api'

export default function GpaGradeMappingPage({ gpaEngineId }) {
  const [mappings, setMappings] = useState([])
  const [loading, setLoading] = useState(false)
  const [modalVisible, setModalVisible] = useState(false)
  const [editingMapping, setEditingMapping] = useState(null)
  const [formData, setFormData] = useState({})

  const fetchMappings = async () => {
    if (!gpaEngineId) return
    setLoading(true)
    try {
      const data = await listGpaGradeMappings(gpaEngineId)
      setMappings(data)
    } catch (err) {
      alert('Failed to load GPA mappings')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => { fetchMappings() }, [gpaEngineId])

  const handleSubmit = async (e) => {
    e.preventDefault()
    try {
      if (editingMapping) {
        await updateGpaGradeMapping(editingMapping.id, formData)
        alert('GPA mapping updated')
      } else {
        await createGpaGradeMapping(gpaEngineId, formData)
        alert('GPA mapping created')
      }
      setModalVisible(false)
      setFormData({})
      setEditingMapping(null)
      fetchMappings()
    } catch (err) {
      alert('Operation failed')
    }
  }

  const handleEdit = (mapping) => {
    setEditingMapping(mapping)
    setFormData(mapping)
    setModalVisible(true)
  }

  const handleDelete = async (id) => {
    if (!window.confirm('Remove this mapping?')) return
    try {
      await updateGpaGradeMapping(id, { is_passing: false })
      alert('Mapping removed')
      fetchMappings()
    } catch (err) {
      alert('Failed to remove')
    }
  }

  return (
    <div style={{ padding: 24 }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 16 }}>
        <h2>GPA Grade Mappings</h2>
        <button onClick={() => { setEditingMapping(null); setFormData({}); setModalVisible(true) }} style={{ padding: '8px 16px', background: '#4f46e5', color: 'white', border: 'none', borderRadius: 4, cursor: 'pointer' }}>
          Add Mapping
        </button>
      </div>
      {loading ? <p>Loading...</p> : (
        <table style={{ width: '100%', borderCollapse: 'collapse' }}>
          <thead>
            <tr style={{ background: '#f3f4f6' }}>
              <th style={{ padding: 8, border: '1px solid #d1d5db', textAlign: 'left' }}>Grade</th>
              <th style={{ padding: 8, border: '1px solid #d1d5db', textAlign: 'left' }}>Grade Point</th>
              <th style={{ padding: 8, border: '1px solid #d1d5db', textAlign: 'left' }}>Min %</th>
              <th style={{ padding: 8, border: '1px solid #d1d5db', textAlign: 'left' }}>Max %</th>
              <th style={{ padding: 8, border: '1px solid #d1d5db', textAlign: 'left' }}>Passing</th>
              <th style={{ padding: 8, border: '1px solid #d1d5db', textAlign: 'left' }}>Description</th>
              <th style={{ padding: 8, border: '1px solid #d1d5db', textAlign: 'left' }}>Actions</th>
            </tr>
          </thead>
          <tbody>
            {mappings.map((m) => (
              <tr key={m.id}>
                <td style={{ padding: 8, border: '1px solid #d1d5db' }}>{m.grade}</td>
                <td style={{ padding: 8, border: '1px solid #d1d5db' }}>{m.grade_point}</td>
                <td style={{ padding: 8, border: '1px solid #d1d5db' }}>{m.min_percentage}</td>
                <td style={{ padding: 8, border: '1px solid #d1d5db' }}>{m.max_percentage}</td>
                <td style={{ padding: 8, border: '1px solid #d1d5db' }}>{m.is_passing ? 'Yes' : 'No'}</td>
                <td style={{ padding: 8, border: '1px solid #d1d5db' }}>{m.description || '-'}</td>
                <td style={{ padding: 8, border: '1px solid #d1d5db' }}>
                  <button onClick={() => handleEdit(m)} style={{ marginRight: 8 }}>Edit</button>
                  <button onClick={() => handleDelete(m.id)} style={{ color: 'red' }}>Remove</button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
      {modalVisible && (
        <div style={{ position: 'fixed', top: 0, left: 0, right: 0, bottom: 0, background: 'rgba(0,0,0,0.5)', display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 1000 }}>
          <div style={{ background: 'white', padding: 24, borderRadius: 8, width: 600, maxHeight: '80vh', overflow: 'auto' }}>
            <h3>{editingMapping ? 'Edit GPA Mapping' : 'Add GPA Mapping'}</h3>
            <form onSubmit={handleSubmit}>
              <div style={{ marginBottom: 12 }}>
                <label>Grade</label>
                <input type='text' value={formData.grade || ''} onChange={(e) => setFormData({...formData, grade: e.target.value})} required style={{ width: '100%', padding: 8, border: '1px solid #d1d5db', borderRadius: 4 }} />
              </div>
              <div style={{ display: 'flex', gap: 12 }}>
                <div style={{ flex: 1 }}>
                  <label>Grade Point</label>
                  <input type='number' step='0.1' value={formData.grade_point || ''} onChange={(e) => setFormData({...formData, grade_point: parseFloat(e.target.value)})} required style={{ width: '100%', padding: 8, border: '1px solid #d1d5db', borderRadius: 4 }} />
                </div>
                <div style={{ flex: 1 }}>
                  <label>Min %</label>
                  <input type='number' value={formData.min_percentage || ''} onChange={(e) => setFormData({...formData, min_percentage: parseFloat(e.target.value)})} required style={{ width: '100%', padding: 8, border: '1px solid #d1d5db', borderRadius: 4 }} />
                </div>
                <div style={{ flex: 1 }}>
                  <label>Max %</label>
                  <input type='number' value={formData.max_percentage || ''} onChange={(e) => setFormData({...formData, max_percentage: parseFloat(e.target.value)})} required style={{ width: '100%', padding: 8, border: '1px solid #d1d5db', borderRadius: 4 }} />
                </div>
              </div>
              <div style={{ marginBottom: 12 }}>
                <label>Description</label>
                <input type='text' value={formData.description || ''} onChange={(e) => setFormData({...formData, description: e.target.value})} style={{ width: '100%', padding: 8, border: '1px solid #d1d5db', borderRadius: 4 }} />
              </div>
              <div style={{ marginBottom: 12 }}>
                <label><input type='checkbox' checked={formData.is_passing !== false} onChange={(e) => setFormData({...formData, is_passing: e.target.checked})} /> Passing</label>
              </div>
              <div style={{ display: 'flex', gap: 8, justifyContent: 'flex-end' }}>
                <button type='button' onClick={() => { setModalVisible(false); setEditingMapping(null) }} style={{ padding: '8px 16px', border: '1px solid #d1d5db', borderRadius: 4, background: 'white', cursor: 'pointer' }}>Cancel</button>
                <button type='submit' style={{ padding: '8px 16px', background: '#4f46e5', color: 'white', border: 'none', borderRadius: 4, cursor: 'pointer' }}>Save</button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  )
}
