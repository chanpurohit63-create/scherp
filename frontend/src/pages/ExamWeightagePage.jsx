import React, { useState, useEffect } from 'react'
import { listExamWeightage, createExamWeightage } from '../api'

export default function ExamWeightagePage() {
  const [configs, setConfigs] = useState([])
  const [loading, setLoading] = useState(false)
  const [modalVisible, setModalVisible] = useState(false)
  const [formData, setFormData] = useState({})

  const fetchConfigs = async () => {
    setLoading(true)
    try {
      const data = await listExamWeightage()
      setConfigs(data)
    } catch (err) {
      alert('Failed to load exam weightage configs')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => { fetchConfigs() }, [])

  const handleSubmit = async (e) => {
    e.preventDefault()
    try {
      await createExamWeightage(formData)
      alert('Weightage config created')
      setModalVisible(false)
      setFormData({})
      fetchConfigs()
    } catch (err) {
      alert('Operation failed')
    }
  }

  return (
    <div style={{ padding: 24 }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 16 }}>
        <h2>Exam Weightage Configuration</h2>
        <button onClick={() => { setFormData({}); setModalVisible(true) }} style={{ padding: '8px 16px', background: '#4f46e5', color: 'white', border: 'none', borderRadius: 4, cursor: 'pointer' }}>
          Add Config
        </button>
      </div>
      {loading ? <p>Loading...</p> : (
        <table style={{ width: '100%', borderCollapse: 'collapse' }}>
          <thead>
            <tr style={{ background: '#f3f4f6' }}>
              <th style={{ padding: 8, border: '1px solid #d1d5db', textAlign: 'left' }}>Academic Year ID</th>
              <th style={{ padding: 8, border: '1px solid #d1d5db', textAlign: 'left' }}>Class ID</th>
              <th style={{ padding: 8, border: '1px solid #d1d5db', textAlign: 'left' }}>Exam Type ID</th>
              <th style={{ padding: 8, border: '1px solid #d1d5db', textAlign: 'left' }}>Weightage</th>
              <th style={{ padding: 8, border: '1px solid #d1d5db', textAlign: 'left' }}>Max Marks</th>
              <th style={{ padding: 8, border: '1px solid #d1d5db', textAlign: 'left' }}>Passing Marks</th>
              <th style={{ padding: 8, border: '1px solid #d1d5db', textAlign: 'left' }}>Active</th>
            </tr>
          </thead>
          <tbody>
            {configs.map((c) => (
              <tr key={c.id}>
                <td style={{ padding: 8, border: '1px solid #d1d5db' }}>{c.academic_year_id}</td>
                <td style={{ padding: 8, border: '1px solid #d1d5db' }}>{c.class_id}</td>
                <td style={{ padding: 8, border: '1px solid #d1d5db' }}>{c.exam_type_id}</td>
                <td style={{ padding: 8, border: '1px solid #d1d5db' }}>{c.weightage}%</td>
                <td style={{ padding: 8, border: '1px solid #d1d5db' }}>{c.max_marks || '-'}</td>
                <td style={{ padding: 8, border: '1px solid #d1d5db' }}>{c.passing_marks || '-'}</td>
                <td style={{ padding: 8, border: '1px solid #d1d5db' }}>{c.is_active ? 'Yes' : 'No'}</td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
      {modalVisible && (
        <div style={{ position: 'fixed', top: 0, left: 0, right: 0, bottom: 0, background: 'rgba(0,0,0,0.5)', display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 1000 }}>
          <div style={{ background: 'white', padding: 24, borderRadius: 8, width: 600, maxHeight: '80vh', overflow: 'auto' }}>
            <h3>Add Weightage Config</h3>
            <form onSubmit={handleSubmit}>
              <div style={{ marginBottom: 12 }}>
                <label>Academic Year ID</label>
                <input type='number' value={formData.academic_year_id || ''} onChange={(e) => setFormData({...formData, academic_year_id: parseInt(e.target.value)})} required style={{ width: '100%', padding: 8, border: '1px solid #d1d5db', borderRadius: 4 }} />
              </div>
              <div style={{ marginBottom: 12 }}>
                <label>Class ID</label>
                <input type='number' value={formData.class_id || ''} onChange={(e) => setFormData({...formData, class_id: parseInt(e.target.value)})} required style={{ width: '100%', padding: 8, border: '1px solid #d1d5db', borderRadius: 4 }} />
              </div>
              <div style={{ marginBottom: 12 }}>
                <label>Exam Type ID</label>
                <input type='number' value={formData.exam_type_id || ''} onChange={(e) => setFormData({...formData, exam_type_id: parseInt(e.target.value)})} required style={{ width: '100%', padding: 8, border: '1px solid #d1d5db', borderRadius: 4 }} />
              </div>
              <div style={{ marginBottom: 12 }}>
                <label>Weightage (%)</label>
                <input type='number' step='0.1' value={formData.weightage || 0} onChange={(e) => setFormData({...formData, weightage: parseFloat(e.target.value)})} required style={{ width: '100%', padding: 8, border: '1px solid #d1d5db', borderRadius: 4 }} />
              </div>
              <div style={{ display: 'flex', gap: 12 }}>
                <div style={{ flex: 1 }}>
                  <label>Max Marks</label>
                  <input type='number' value={formData.max_marks || ''} onChange={(e) => setFormData({...formData, max_marks: parseFloat(e.target.value)})} style={{ width: '100%', padding: 8, border: '1px solid #d1d5db', borderRadius: 4 }} />
                </div>
                <div style={{ flex: 1 }}>
                  <label>Passing Marks</label>
                  <input type='number' value={formData.passing_marks || ''} onChange={(e) => setFormData({...formData, passing_marks: parseFloat(e.target.value)})} style={{ width: '100%', padding: 8, border: '1px solid #d1d5db', borderRadius: 4 }} />
                </div>
              </div>
              <div style={{ display: 'flex', gap: 8, justifyContent: 'flex-end' }}>
                <button type='button' onClick={() => { setModalVisible(false) }} style={{ padding: '8px 16px', border: '1px solid #d1d5db', borderRadius: 4, background: 'white', cursor: 'pointer' }}>Cancel</button>
                <button type='submit' style={{ padding: '8px 16px', background: '#4f46e5', color: 'white', border: 'none', borderRadius: 4, cursor: 'pointer' }}>Save</button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  )
}
