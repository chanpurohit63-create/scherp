import React, { useState, useEffect } from 'react'
import { listGpaEngines, createGpaEngine, updateGpaEngine, deleteResource } from '../api'

const GPA_SCALE_TYPES = [
  { value: '4_point', label: '4 Point Scale' },
  { value: '5_point', label: '5 Point Scale' },
  { value: '10_point', label: '10 Point Scale' },
  { value: 'percentage', label: 'Percentage Based' },
  { value: 'weighted', label: 'Weighted GPA' },
  { value: 'credit_based', label: 'Credit Based GPA' },
]

export default function GpaEnginePage() {
  const [engines, setEngines] = useState([])
  const [loading, setLoading] = useState(false)
  const [modalVisible, setModalVisible] = useState(false)
  const [editingEngine, setEditingEngine] = useState(null)
  const [formData, setFormData] = useState({})

  const fetchEngines = async () => {
    setLoading(true)
    try {
      const data = await listGpaEngines()
      setEngines(data)
    } catch (err) {
      alert('Failed to load GPA engines')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => { fetchEngines() }, [])

  const handleSubmit = async (e) => {
    e.preventDefault()
    try {
      if (editingEngine) {
        await updateGpaEngine(editingEngine.id, formData)
        alert('GPA engine updated')
      } else {
        await createGpaEngine(formData)
        alert('GPA engine created')
      }
      setModalVisible(false)
      setFormData({})
      setEditingEngine(null)
      fetchEngines()
    } catch (err) {
      alert('Operation failed')
    }
  }

  const handleDelete = async (id) => {
    if (!window.confirm('Delete this GPA engine?')) return
    try {
      await deleteResource(null, 'gpa-engines', id)
      alert('GPA engine deleted')
      fetchEngines()
    } catch (err) {
      alert('Failed to delete')
    }
  }

  const handleEdit = (engine) => {
    setEditingEngine(engine)
    setFormData(engine)
    setModalVisible(true)
  }

  return (
    <div style={{ padding: 24 }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 16 }}>
        <h2>GPA Engines</h2>
        <button onClick={() => { setEditingEngine(null); setFormData({}); setModalVisible(true) }} style={{ padding: '8px 16px', background: '#4f46e5', color: 'white', border: 'none', borderRadius: 4, cursor: 'pointer' }}>
          Create GPA Engine
        </button>
      </div>
      {loading ? <p>Loading...</p> : (
        <table style={{ width: '100%', borderCollapse: 'collapse' }}>
          <thead>
            <tr style={{ background: '#f3f4f6' }}>
              <th style={{ padding: 8, border: '1px solid #d1d5db', textAlign: 'left' }}>Name</th>
              <th style={{ padding: 8, border: '1px solid #d1d5db', textAlign: 'left' }}>Scale Type</th>
              <th style={{ padding: 8, border: '1px solid #d1d5db', textAlign: 'left' }}>Max GPA</th>
              <th style={{ padding: 8, border: '1px solid #d1d5db', textAlign: 'left' }}>Min GPA</th>
              <th style={{ padding: 8, border: '1px solid #d1d5db', textAlign: 'left' }}>Credit Based</th>
              <th style={{ padding: 8, border: '1px solid #d1d5db', textAlign: 'left' }}>Weighted</th>
              <th style={{ padding: 8, border: '1px solid #d1d5db', textAlign: 'left' }}>Active</th>
              <th style={{ padding: 8, border: '1px solid #d1d5db', textAlign: 'left' }}>Actions</th>
            </tr>
          </thead>
          <tbody>
            {engines.map((e) => (
              <tr key={e.id}>
                <td style={{ padding: 8, border: '1px solid #d1d5db' }}>{e.name}</td>
                <td style={{ padding: 8, border: '1px solid #d1d5db' }}>{e.scale_type}</td>
                <td style={{ padding: 8, border: '1px solid #d1d5db' }}>{e.max_gpa}</td>
                <td style={{ padding: 8, border: '1px solid #d1d5db' }}>{e.min_gpa}</td>
                <td style={{ padding: 8, border: '1px solid #d1d5db' }}>{e.credit_based ? 'Yes' : 'No'}</td>
                <td style={{ padding: 8, border: '1px solid #d1d5db' }}>{e.weighted ? 'Yes' : 'No'}</td>
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
            <h3>{editingEngine ? 'Edit GPA Engine' : 'Create GPA Engine'}</h3>
            <form onSubmit={handleSubmit}>
              <div style={{ marginBottom: 12 }}>
                <label>Name</label>
                <input type='text' value={formData.name || ''} onChange={(e) => setFormData({...formData, name: e.target.value})} required style={{ width: '100%', padding: 8, border: '1px solid #d1d5db', borderRadius: 4 }} />
              </div>
              <div style={{ marginBottom: 12 }}>
                <label>Scale Type</label>
                <select value={formData.scale_type || '4_point'} onChange={(e) => setFormData({...formData, scale_type: e.target.value})} style={{ width: '100%', padding: 8, border: '1px solid #d1d5db', borderRadius: 4 }}>
                  {GPA_SCALE_TYPES.map((t) => <option key={t.value} value={t.value}>{t.label}</option>)}
                </select>
              </div>
              <div style={{ display: 'flex', gap: 12 }}>
                <div style={{ flex: 1 }}>
                  <label>Max GPA</label>
                  <input type='number' step='0.1' value={formData.max_gpa || 4.0} onChange={(e) => setFormData({...formData, max_gpa: parseFloat(e.target.value)})} style={{ width: '100%', padding: 8, border: '1px solid #d1d5db', borderRadius: 4 }} />
                </div>
                <div style={{ flex: 1 }}>
                  <label>Min GPA</label>
                  <input type='number' step='0.1' value={formData.min_gpa || 0.0} onChange={(e) => setFormData({...formData, min_gpa: parseFloat(e.target.value)})} style={{ width: '100%', padding: 8, border: '1px solid #d1d5db', borderRadius: 4 }} />
                </div>
                <div style={{ flex: 1 }}>
                  <label>Decimals</label>
                  <input type='number' value={formData.grade_point_decimals || 2} onChange={(e) => setFormData({...formData, grade_point_decimals: parseInt(e.target.value)})} style={{ width: '100%', padding: 8, border: '1px solid #d1d5db', borderRadius: 4 }} />
                </div>
              </div>
              <div style={{ marginBottom: 12 }}>
                <label><input type='checkbox' checked={formData.credit_based} onChange={(e) => setFormData({...formData, credit_based: e.target.checked})} /> Credit Based</label>
              </div>
              <div style={{ marginBottom: 12 }}>
                <label><input type='checkbox' checked={formData.weighted} onChange={(e) => setFormData({...formData, weighted: e.target.checked})} /> Weighted</label>
              </div>
              <div style={{ marginBottom: 12 }}>
                <label>Formula Config (JSON)</label>
                <textarea value={formData.formula_config || ''} onChange={(e) => setFormData({...formData, formula_config: e.target.value})} rows={3} style={{ width: '100%', padding: 8, border: '1px solid #d1d5db', borderRadius: 4 }} />
              </div>
              <div style={{ marginBottom: 12 }}>
                <label><input type='checkbox' checked={formData.is_active !== false} onChange={(e) => setFormData({...formData, is_active: e.target.checked})} /> Active</label>
              </div>
              <div style={{ display: 'flex', gap: 8, justifyContent: 'flex-end' }}>
                <button type='button' onClick={() => { setModalVisible(false); setEditingEngine(null) }} style={{ padding: '8px 16px', border: '1px solid #d1d5db', borderRadius: 4, background: 'white', cursor: 'pointer' }}>Cancel</button>
                <button type='submit' style={{ padding: '8px 16px', background: '#4f46e5', color: 'white', border: 'none', borderRadius: 4, cursor: 'pointer' }}>Save</button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  )
}
