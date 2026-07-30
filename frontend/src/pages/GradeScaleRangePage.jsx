import React, { useState, useEffect } from 'react'
import { listGradeScaleRanges, createGradeScaleRange, updateGradeScaleRange } from '../api'

export default function GradeScaleRangePage({ gradeScaleId }) {
  const [ranges, setRanges] = useState([])
  const [loading, setLoading] = useState(false)
  const [modalVisible, setModalVisible] = useState(false)
  const [editingRange, setEditingRange] = useState(null)
  const [formData, setFormData] = useState({})

  const fetchRanges = async () => {
    if (!gradeScaleId) return
    setLoading(true)
    try {
      const data = await listGradeScaleRanges(gradeScaleId)
      setRanges(data)
    } catch (err) {
      alert('Failed to load grade ranges')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => { fetchRanges() }, [gradeScaleId])

  const handleSubmit = async (e) => {
    e.preventDefault()
    try {
      if (editingRange) {
        await updateGradeScaleRange(editingRange.id, formData)
        alert('Grade range updated')
      } else {
        await createGradeScaleRange(gradeScaleId, formData)
        alert('Grade range created')
      }
      setModalVisible(false)
      setFormData({})
      setEditingRange(null)
      fetchRanges()
    } catch (err) {
      alert('Operation failed')
    }
  }

  const handleEdit = (range) => {
    setEditingRange(range)
    setFormData(range)
    setModalVisible(true)
  }

  const handleDelete = async (id) => {
    if (!window.confirm('Remove this range?')) return
    try {
      await updateGradeScaleRange(id, { is_passing: false })
      alert('Range removed')
      fetchRanges()
    } catch (err) {
      alert('Failed to remove')
    }
  }

  return (
    <div style={{ padding: 24 }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 16 }}>
        <h2>Grade Scale Ranges</h2>
        <button onClick={() => { setEditingRange(null); setFormData({}); setModalVisible(true) }} style={{ padding: '8px 16px', background: '#4f46e5', color: 'white', border: 'none', borderRadius: 4, cursor: 'pointer' }}>
          Add Range
        </button>
      </div>
      {loading ? <p>Loading...</p> : (
        <table style={{ width: '100%', borderCollapse: 'collapse' }}>
          <thead>
            <tr style={{ background: '#f3f4f6' }}>
              <th style={{ padding: 8, border: '1px solid #d1d5db', textAlign: 'left' }}>Grade</th>
              <th style={{ padding: 8, border: '1px solid #d1d5db', textAlign: 'left' }}>Grade Point</th>
              <th style={{ padding: 8, border: '1px solid #d1d5db', textAlign: 'left' }}>Min Mark</th>
              <th style={{ padding: 8, border: '1px solid #d1d5db', textAlign: 'left' }}>Max Mark</th>
              <th style={{ padding: 8, border: '1px solid #d1d5db', textAlign: 'left' }}>Passing</th>
              <th style={{ padding: 8, border: '1px solid #d1d5db', textAlign: 'left' }}>Description</th>
              <th style={{ padding: 8, border: '1px solid #d1d5db', textAlign: 'left' }}>Actions</th>
            </tr>
          </thead>
          <tbody>
            {ranges.map((r) => (
              <tr key={r.id}>
                <td style={{ padding: 8, border: '1px solid #d1d5db' }}>{r.grade}</td>
                <td style={{ padding: 8, border: '1px solid #d1d5db' }}>{r.grade_point}</td>
                <td style={{ padding: 8, border: '1px solid #d1d5db' }}>{r.min_mark}</td>
                <td style={{ padding: 8, border: '1px solid #d1d5db' }}>{r.max_mark}</td>
                <td style={{ padding: 8, border: '1px solid #d1d5db' }}>{r.is_passing ? 'Yes' : 'No'}</td>
                <td style={{ padding: 8, border: '1px solid #d1d5db' }}>{r.description || '-'}</td>
                <td style={{ padding: 8, border: '1px solid #d1d5db' }}>
                  <button onClick={() => handleEdit(r)} style={{ marginRight: 8 }}>Edit</button>
                  <button onClick={() => handleDelete(r.id)} style={{ color: 'red' }}>Remove</button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
      {modalVisible && (
        <div style={{ position: 'fixed', top: 0, left: 0, right: 0, bottom: 0, background: 'rgba(0,0,0,0.5)', display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 1000 }}>
          <div style={{ background: 'white', padding: 24, borderRadius: 8, width: 600, maxHeight: '80vh', overflow: 'auto' }}>
            <h3>{editingRange ? 'Edit Grade Range' : 'Add Grade Range'}</h3>
            <form onSubmit={handleSubmit}>
              <div style={{ marginBottom: 12 }}>
                <label>Grade</label>
                <input type='text' value={formData.grade || ''} onChange={(e) => setFormData({...formData, grade: e.target.value})} required style={{ width: '100%', padding: 8, border: '1px solid #d1d5db', borderRadius: 4 }} />
              </div>
              <div style={{ marginBottom: 12 }}>
                <label>Grade Point</label>
                <input type='number' step='0.1' value={formData.grade_point || ''} onChange={(e) => setFormData({...formData, grade_point: parseFloat(e.target.value)})} style={{ width: '100%', padding: 8, border: '1px solid #d1d5db', borderRadius: 4 }} />
              </div>
              <div style={{ display: 'flex', gap: 12 }}>
                <div style={{ flex: 1 }}>
                  <label>Min Mark</label>
                  <input type='number' value={formData.min_mark || ''} onChange={(e) => setFormData({...formData, min_mark: parseFloat(e.target.value)})} required style={{ width: '100%', padding: 8, border: '1px solid #d1d5db', borderRadius: 4 }} />
                </div>
                <div style={{ flex: 1 }}>
                  <label>Max Mark</label>
                  <input type='number' value={formData.max_mark || ''} onChange={(e) => setFormData({...formData, max_mark: parseFloat(e.target.value)})} required style={{ width: '100%', padding: 8, border: '1px solid #d1d5db', borderRadius: 4 }} />
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
                <button type='button' onClick={() => { setModalVisible(false); setEditingRange(null) }} style={{ padding: '8px 16px', border: '1px solid #d1d5db', borderRadius: 4, background: 'white', cursor: 'pointer' }}>Cancel</button>
                <button type='submit' style={{ padding: '8px 16px', background: '#4f46e5', color: 'white', border: 'none', borderRadius: 4, cursor: 'pointer' }}>Save</button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  )
}
