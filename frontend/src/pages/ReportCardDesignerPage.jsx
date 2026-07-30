import React, { useState, useEffect } from 'react'
import { listReportCardComponents, createReportCardComponent, updateReportCardComponent, deleteReportCardComponent } from '../api'

const COMPONENT_TYPES = [
  { value: 'logo', label: 'Logo' },
  { value: 'student_photo', label: 'Student Photo' },
  { value: 'qr_code', label: 'QR Code' },
  { value: 'signature', label: 'Signature' },
  { value: 'subject_table', label: 'Subject Table' },
  { value: 'chart', label: 'Chart' },
  { value: 'remarks', label: 'Remarks' },
  { value: 'attendance', label: 'Attendance' },
  { value: 'watermark', label: 'Watermark' },
  { value: 'header', label: 'Header' },
  { value: 'footer', label: 'Footer' },
  { value: 'custom_text', label: 'Custom Text' },
  { value: 'custom_image', label: 'Custom Image' },
]

export default function ReportCardDesignerPage() {
  const [components, setComponents] = useState([])
  const [loading, setLoading] = useState(false)
  const [modalVisible, setModalVisible] = useState(false)
  const [editingComponent, setEditingComponent] = useState(null)
  const [formData, setFormData] = useState({})

  const fetchComponents = async () => {
    setLoading(true)
    try {
      const data = await listReportCardComponents()
      setComponents(data)
    } catch (err) {
      alert('Failed to load components')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => { fetchComponents() }, [])

  const handleSubmit = async (e) => {
    e.preventDefault()
    try {
      if (editingComponent) {
        await updateReportCardComponent(editingComponent.id, formData)
        alert('Component updated')
      } else {
        await createReportCardComponent(formData)
        alert('Component added')
      }
      setModalVisible(false)
      setFormData({})
      setEditingComponent(null)
      fetchComponents()
    } catch (err) {
      alert('Operation failed')
    }
  }

  const handleDelete = async (id) => {
    if (!window.confirm('Delete this component?')) return
    try {
      await deleteReportCardComponent(id)
      alert('Component deleted')
      fetchComponents()
    } catch (err) {
      alert('Failed to delete')
    }
  }

  const handleEdit = (component) => {
    setEditingComponent(component)
    setFormData(component)
    setModalVisible(true)
  }

  return (
    <div style={{ padding: 24 }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 16 }}>
        <h2>Report Card Designer</h2>
        <button onClick={() => { setEditingComponent(null); setFormData({}); setModalVisible(true) }} style={{ padding: '8px 16px', background: '#4f46e5', color: 'white', border: 'none', borderRadius: 4, cursor: 'pointer' }}>
          Add Component
        </button>
      </div>
      {loading ? <p>Loading...</p> : (
        <div style={{ display: 'flex', gap: 16 }}>
          <div style={{ flex: 1 }}>
            <h3>Components</h3>
            {components.map((c) => (
              <div key={c.id} style={{ padding: 12, marginBottom: 8, background: '#fafafa', border: '1px solid #d1d5db', borderRadius: 4, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <div>
                  <span style={{ marginRight: 8 }}>{c.component_type}</span>
                  <strong>{c.label}</strong>
                  <span style={{ marginLeft: 8, color: '#666' }}>({c.x_position}%, {c.y_position}%, {c.width}x{c.height})</span>
                </div>
                <div>
                  <button onClick={() => handleEdit(c)} style={{ marginRight: 8 }}>Edit</button>
                  <button onClick={() => handleDelete(c.id)} style={{ color: 'red' }}>Delete</button>
                </div>
              </div>
            ))}
          </div>
          <div style={{ flex: 1 }}>
            <h3>Live Preview</h3>
            <div style={{ border: '2px dashed #d1d5db', padding: 24, textAlign: 'center', color: '#999', minHeight: 400 }}>
              <p>Live preview of the report card template</p>
              <p>Components: {components.length}</p>
            </div>
          </div>
        </div>
      )}
      {modalVisible && (
        <div style={{ position: 'fixed', top: 0, left: 0, right: 0, bottom: 0, background: 'rgba(0,0,0,0.5)', display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 1000 }}>
          <div style={{ background: 'white', padding: 24, borderRadius: 8, width: 700, maxHeight: '80vh', overflow: 'auto' }}>
            <h3>{editingComponent ? 'Edit Component' : 'Add Component'}</h3>
            <form onSubmit={handleSubmit}>
              <div style={{ marginBottom: 12 }}>
                <label>Component Type</label>
                <select value={formData.component_type || ''} onChange={(e) => setFormData({...formData, component_type: e.target.value})} required style={{ width: '100%', padding: 8, border: '1px solid #d1d5db', borderRadius: 4 }}>
                  <option value=''>Select type</option>
                  {COMPONENT_TYPES.map((t) => <option key={t.value} value={t.value}>{t.label}</option>)}
                </select>
              </div>
              <div style={{ marginBottom: 12 }}>
                <label>Label</label>
                <input type='text' value={formData.label || ''} onChange={(e) => setFormData({...formData, label: e.target.value})} required style={{ width: '100%', padding: 8, border: '1px solid #d1d5db', borderRadius: 4 }} />
              </div>
              <div style={{ display: 'flex', gap: 12 }}>
                <div style={{ flex: 1 }}>
                  <label>X Position (%)</label>
                  <input type='number' value={formData.x_position || 0} onChange={(e) => setFormData({...formData, x_position: parseFloat(e.target.value)})} style={{ width: '100%', padding: 8, border: '1px solid #d1d5db', borderRadius: 4 }} />
                </div>
                <div style={{ flex: 1 }}>
                  <label>Y Position (%)</label>
                  <input type='number' value={formData.y_position || 0} onChange={(e) => setFormData({...formData, y_position: parseFloat(e.target.value)})} style={{ width: '100%', padding: 8, border: '1px solid #d1d5db', borderRadius: 4 }} />
                </div>
                <div style={{ flex: 1 }}>
                  <label>Width (%)</label>
                  <input type='number' value={formData.width || 100} onChange={(e) => setFormData({...formData, width: parseFloat(e.target.value)})} style={{ width: '100%', padding: 8, border: '1px solid #d1d5db', borderRadius: 4 }} />
                </div>
                <div style={{ flex: 1 }}>
                  <label>Height (%)</label>
                  <input type='number' value={formData.height || 50} onChange={(e) => setFormData({...formData, height: parseFloat(e.target.value)})} style={{ width: '100%', padding: 8, border: '1px solid #d1d5db', borderRadius: 4 }} />
                </div>
              </div>
              <div style={{ display: 'flex', gap: 12, marginTop: 12 }}>
                <div style={{ flex: 1 }}>
                  <label>Font Size</label>
                  <input type='number' value={formData.font_size || ''} onChange={(e) => setFormData({...formData, font_size: parseInt(e.target.value)})} style={{ width: '100%', padding: 8, border: '1px solid #d1d5db', borderRadius: 4 }} />
                </div>
                <div style={{ flex: 1 }}>
                  <label>Font Color</label>
                  <input type='text' value={formData.font_color || ''} onChange={(e) => setFormData({...formData, font_color: e.target.value})} style={{ width: '100%', padding: 8, border: '1px solid #d1d5db', borderRadius: 4 }} />
                </div>
                <div style={{ flex: 1 }}>
                  <label>Font Family</label>
                  <input type='text' value={formData.font_family || ''} onChange={(e) => setFormData({...formData, font_family: e.target.value})} style={{ width: '100%', padding: 8, border: '1px solid #d1d5db', borderRadius: 4 }} />
                </div>
                <div style={{ flex: 1 }}>
                  <label>Font Weight</label>
                  <select value={formData.font_weight || ''} onChange={(e) => setFormData({...formData, font_weight: e.target.value})} style={{ width: '100%', padding: 8, border: '1px solid #d1d5db', borderRadius: 4 }}>
                    <option value=''>Normal</option>
                    <option value='bold'>Bold</option>
                  </select>
                </div>
              </div>
              <div style={{ display: 'flex', gap: 12, marginTop: 12 }}>
                <div style={{ flex: 1 }}>
                  <label>Border Radius</label>
                  <input type='number' value={formData.border_radius || ''} onChange={(e) => setFormData({...formData, border_radius: parseInt(e.target.value)})} style={{ width: '100%', padding: 8, border: '1px solid #d1d5db', borderRadius: 4 }} />
                </div>
                <div style={{ flex: 1 }}>
                  <label>Border Width</label>
                  <input type='number' value={formData.border_width || ''} onChange={(e) => setFormData({...formData, border_width: parseInt(e.target.value)})} style={{ width: '100%', padding: 8, border: '1px solid #d1d5db', borderRadius: 4 }} />
                </div>
                <div style={{ flex: 1 }}>
                  <label>Border Color</label>
                  <input type='text' value={formData.border_color || ''} onChange={(e) => setFormData({...formData, border_color: e.target.value})} style={{ width: '100%', padding: 8, border: '1px solid #d1d5db', borderRadius: 4 }} />
                </div>
                <div style={{ flex: 1 }}>
                  <label>Background Color</label>
                  <input type='text' value={formData.background_color || ''} onChange={(e) => setFormData({...formData, background_color: e.target.value})} style={{ width: '100%', padding: 8, border: '1px solid #d1d5db', borderRadius: 4 }} />
                </div>
              </div>
              <div style={{ marginTop: 12 }}>
                <label>Data Source</label>
                <input type='text' value={formData.data_source || ''} onChange={(e) => setFormData({...formData, data_source: e.target.value})} style={{ width: '100%', padding: 8, border: '1px solid #d1d5db', borderRadius: 4 }} />
              </div>
              <div style={{ marginTop: 12 }}>
                <label>Default Value</label>
                <input type='text' value={formData.default_value || ''} onChange={(e) => setFormData({...formData, default_value: e.target.value})} style={{ width: '100%', padding: 8, border: '1px solid #d1d5db', borderRadius: 4 }} />
              </div>
              <div style={{ marginTop: 12 }}>
                <label>Sort Order</label>
                <input type='number' value={formData.sort_order || 0} onChange={(e) => setFormData({...formData, sort_order: parseInt(e.target.value)})} style={{ width: '100%', padding: 8, border: '1px solid #d1d5db', borderRadius: 4 }} />
              </div>
              <div style={{ display: 'flex', gap: 8, justifyContent: 'flex-end', marginTop: 16 }}>
                <button type='button' onClick={() => { setModalVisible(false); setEditingComponent(null) }} style={{ padding: '8px 16px', border: '1px solid #d1d5db', borderRadius: 4, background: 'white', cursor: 'pointer' }}>Cancel</button>
                <button type='submit' style={{ padding: '8px 16px', background: '#4f46e5', color: 'white', border: 'none', borderRadius: 4, cursor: 'pointer' }}>Save</button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  )
}
