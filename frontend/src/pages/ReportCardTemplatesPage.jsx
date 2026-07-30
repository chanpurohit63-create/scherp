import React, { useState, useEffect } from 'react'
import { listReportCardTemplates, createReportCardTemplate, updateReportCardTemplate, archiveReportCardTemplate, duplicateReportCardTemplate } from '../api'

const TEMPLATE_TYPES = [
  { value: 'standard', label: 'Standard' },
  { value: 'cbse', label: 'CBSE' },
  { value: 'icse', label: 'ICSE' },
  { value: 'state_board', label: 'State Board' },
  { value: 'cambridge', label: 'Cambridge' },
  { value: 'ib', label: 'IB' },
  { value: 'montessori', label: 'Montessori' },
  { value: 'preschool', label: 'Preschool' },
  { value: 'custom', label: 'Custom' },
]

export default function ReportCardTemplatesPage() {
  const [templates, setTemplates] = useState([])
  const [loading, setLoading] = useState(false)
  const [modalVisible, setModalVisible] = useState(false)
  const [editingTemplate, setEditingTemplate] = useState(null)
  const [formData, setFormData] = useState({})

  const fetchTemplates = async () => {
    setLoading(true)
    try {
      const data = await listReportCardTemplates()
      setTemplates(data)
    } catch (err) {
      alert('Failed to load templates')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => { fetchTemplates() }, [])

  const handleSubmit = async (e) => {
    e.preventDefault()
    try {
      if (editingTemplate) {
        await updateReportCardTemplate(editingTemplate.id, formData)
        alert('Template updated')
      } else {
        await createReportCardTemplate(formData)
        alert('Template created')
      }
      setModalVisible(false)
      setFormData({})
      setEditingTemplate(null)
      fetchTemplates()
    } catch (err) {
      alert('Operation failed')
    }
  }

  const handleArchive = async (id) => {
    try {
      await archiveReportCardTemplate(id)
      alert('Template archived')
      fetchTemplates()
    } catch (err) {
      alert('Failed to archive')
    }
  }

  const handleDuplicate = async (id) => {
    try {
      await duplicateReportCardTemplate(id)
      alert('Template duplicated')
      fetchTemplates()
    } catch (err) {
      alert('Failed to duplicate')
    }
  }

  const handleEdit = (template) => {
    setEditingTemplate(template)
    setFormData(template)
    setModalVisible(true)
  }

  return (
    <div style={{ padding: 24 }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 16 }}>
        <h2>Report Card Templates</h2>
        <button onClick={() => { setEditingTemplate(null); setFormData({}); setModalVisible(true) }} style={{ padding: '8px 16px', background: '#4f46e5', color: 'white', border: 'none', borderRadius: 4, cursor: 'pointer' }}>
          Create Template
        </button>
      </div>
      {loading ? <p>Loading...</p> : (
        <table style={{ width: '100%', borderCollapse: 'collapse' }}>
          <thead>
            <tr style={{ background: '#f3f4f6' }}>
              <th style={{ padding: 8, border: '1px solid #d1d5db', textAlign: 'left' }}>Name</th>
              <th style={{ padding: 8, border: '1px solid #d1d5db', textAlign: 'left' }}>Type</th>
              <th style={{ padding: 8, border: '1px solid #d1d5db', textAlign: 'left' }}>Version</th>
              <th style={{ padding: 8, border: '1px solid #d1d5db', textAlign: 'left' }}>Default</th>
              <th style={{ padding: 8, border: '1px solid #d1d5db', textAlign: 'left' }}>Archived</th>
              <th style={{ padding: 8, border: '1px solid #d1d5db', textAlign: 'left' }}>Actions</th>
            </tr>
          </thead>
          <tbody>
            {templates.map((t) => (
              <tr key={t.id}>
                <td style={{ padding: 8, border: '1px solid #d1d5db' }}>{t.name}</td>
                <td style={{ padding: 8, border: '1px solid #d1d5db' }}><span style={{ background: '#e0e7ff', padding: '2px 8px', borderRadius: 12 }}>{t.template_type}</span></td>
                <td style={{ padding: 8, border: '1px solid #d1d5db' }}>{t.version}</td>
                <td style={{ padding: 8, border: '1px solid #d1d5db' }}>{t.is_default ? 'Yes' : 'No'}</td>
                <td style={{ padding: 8, border: '1px solid #d1d5db' }}>{t.is_archived ? 'Yes' : 'No'}</td>
                <td style={{ padding: 8, border: '1px solid #d1d5db' }}>
                  <button onClick={() => handleEdit(t)} style={{ marginRight: 8 }}>Edit</button>
                  <button onClick={() => handleDuplicate(t.id)} style={{ marginRight: 8 }}>Duplicate</button>
                  <button onClick={() => handleArchive(t.id)} style={{ color: 'red' }}>Archive</button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
      {modalVisible && (
        <div style={{ position: 'fixed', top: 0, left: 0, right: 0, bottom: 0, background: 'rgba(0,0,0,0.5)', display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 1000 }}>
          <div style={{ background: 'white', padding: 24, borderRadius: 8, width: 600, maxHeight: '80vh', overflow: 'auto' }}>
            <h3>{editingTemplate ? 'Edit Template' : 'Create Template'}</h3>
            <form onSubmit={handleSubmit}>
              <div style={{ marginBottom: 12 }}>
                <label>Template Name</label>
                <input type='text' value={formData.name || ''} onChange={(e) => setFormData({...formData, name: e.target.value})} required style={{ width: '100%', padding: 8, border: '1px solid #d1d5db', borderRadius: 4 }} />
              </div>
              <div style={{ marginBottom: 12 }}>
                <label>Description</label>
                <textarea value={formData.description || ''} onChange={(e) => setFormData({...formData, description: e.target.value})} style={{ width: '100%', padding: 8, border: '1px solid #d1d5db', borderRadius: 4 }} />
              </div>
              <div style={{ marginBottom: 12 }}>
                <label>Template Type</label>
                <select value={formData.template_type || 'standard'} onChange={(e) => setFormData({...formData, template_type: e.target.value})} style={{ width: '100%', padding: 8, border: '1px solid #d1d5db', borderRadius: 4 }}>
                  {TEMPLATE_TYPES.map((t) => <option key={t.value} value={t.value}>{t.label}</option>)}
                </select>
              </div>
              <div style={{ marginBottom: 12 }}>
                <label>Config (JSON)</label>
                <textarea value={formData.config || ''} onChange={(e) => setFormData({...formData, config: e.target.value})} rows={4} style={{ width: '100%', padding: 8, border: '1px solid #d1d5db', borderRadius: 4 }} />
              </div>
              <div style={{ marginBottom: 12 }}>
                <label>CSS Config (JSON)</label>
                <textarea value={formData.css_config || ''} onChange={(e) => setFormData({...formData, css_config: e.target.value})} rows={4} style={{ width: '100%', padding: 8, border: '1px solid #d1d5db', borderRadius: 4 }} />
              </div>
              <div style={{ display: 'flex', gap: 8, justifyContent: 'flex-end' }}>
                <button type='button' onClick={() => { setModalVisible(false); setEditingTemplate(null) }} style={{ padding: '8px 16px', border: '1px solid #d1d5db', borderRadius: 4, background: 'white', cursor: 'pointer' }}>Cancel</button>
                <button type='submit' style={{ padding: '8px 16px', background: '#4f46e5', color: 'white', border: 'none', borderRadius: 4, cursor: 'pointer' }}>Save</button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  )
}
