import React, { useState, useEffect } from 'react'
import { listSubjectCategories, createSubjectCategory, updateSubjectCategory, deleteSubjectCategory } from '../api'

export default function SubjectCategoryPage() {
  const [categories, setCategories] = useState([])
  const [loading, setLoading] = useState(false)
  const [modalVisible, setModalVisible] = useState(false)
  const [editingCategory, setEditingCategory] = useState(null)
  const [formData, setFormData] = useState({})

  const fetchCategories = async () => {
    setLoading(true)
    try {
      const data = await listSubjectCategories()
      setCategories(data)
    } catch (err) {
      alert('Failed to load categories')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => { fetchCategories() }, [])

  const handleSubmit = async (e) => {
    e.preventDefault()
    try {
      if (editingCategory) {
        await updateSubjectCategory(editingCategory.id, formData)
        alert('Category updated')
      } else {
        await createSubjectCategory(formData)
        alert('Category created')
      }
      setModalVisible(false)
      setFormData({})
      setEditingCategory(null)
      fetchCategories()
    } catch (err) {
      alert('Operation failed')
    }
  }

  const handleDelete = async (id) => {
    if (!window.confirm('Delete this category?')) return
    try {
      await deleteSubjectCategory(id)
      alert('Category deleted')
      fetchCategories()
    } catch (err) {
      alert('Failed to delete')
    }
  }

  const handleEdit = (category) => {
    setEditingCategory(category)
    setFormData(category)
    setModalVisible(true)
  }

  return (
    <div style={{ padding: 24 }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 16 }}>
        <h2>Subject Categories</h2>
        <button onClick={() => { setEditingCategory(null); setFormData({}); setModalVisible(true) }} style={{ padding: '8px 16px', background: '#4f46e5', color: 'white', border: 'none', borderRadius: 4, cursor: 'pointer' }}>
          Create Category
        </button>
      </div>
      {loading ? <p>Loading...</p> : (
        <table style={{ width: '100%', borderCollapse: 'collapse' }}>
          <thead>
            <tr style={{ background: '#f3f4f6' }}>
              <th style={{ padding: 8, border: '1px solid #d1d5db', textAlign: 'left' }}>Name</th>
              <th style={{ padding: 8, border: '1px solid #d1d5db', textAlign: 'left' }}>Code</th>
              <th style={{ padding: 8, border: '1px solid #d1d5db', textAlign: 'left' }}>Description</th>
              <th style={{ padding: 8, border: '1px solid #d1d5db', textAlign: 'left' }}>Color</th>
              <th style={{ padding: 8, border: '1px solid #d1d5db', textAlign: 'left' }}>Active</th>
              <th style={{ padding: 8, border: '1px solid #d1d5db', textAlign: 'left' }}>Sort Order</th>
              <th style={{ padding: 8, border: '1px solid #d1d5db', textAlign: 'left' }}>Actions</th>
            </tr>
          </thead>
          <tbody>
            {categories.map((c) => (
              <tr key={c.id}>
                <td style={{ padding: 8, border: '1px solid #d1d5db' }}>{c.name}</td>
                <td style={{ padding: 8, border: '1px solid #d1d5db' }}>{c.code || '-'}</td>
                <td style={{ padding: 8, border: '1px solid #d1d5db' }}>{c.description || '-'}</td>
                <td style={{ padding: 8, border: '1px solid #d1d5db' }}>{c.color ? <span style={{ background: c.color, padding: '2px 8px', borderRadius: 4, color: '#fff' }}>{c.color}</span> : '-'}</td>
                <td style={{ padding: 8, border: '1px solid #d1d5db' }}>{c.is_active ? 'Yes' : 'No'}</td>
                <td style={{ padding: 8, border: '1px solid #d1d5db' }}>{c.sort_order}</td>
                <td style={{ padding: 8, border: '1px solid #d1d5db' }}>
                  <button onClick={() => handleEdit(c)} style={{ marginRight: 8 }}>Edit</button>
                  <button onClick={() => handleDelete(c.id)} style={{ color: 'red' }}>Delete</button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
      {modalVisible && (
        <div style={{ position: 'fixed', top: 0, left: 0, right: 0, bottom: 0, background: 'rgba(0,0,0,0.5)', display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 1000 }}>
          <div style={{ background: 'white', padding: 24, borderRadius: 8, width: 600, maxHeight: '80vh', overflow: 'auto' }}>
            <h3>{editingCategory ? 'Edit Category' : 'Create Category'}</h3>
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
                <label>Description</label>
                <textarea value={formData.description || ''} onChange={(e) => setFormData({...formData, description: e.target.value})} style={{ width: '100%', padding: 8, border: '1px solid #d1d5db', borderRadius: 4 }} />
              </div>
              <div style={{ marginBottom: 12 }}>
                <label>Color</label>
                <input type='text' value={formData.color || ''} onChange={(e) => setFormData({...formData, color: e.target.value})} style={{ width: '100%', padding: 8, border: '1px solid #d1d5db', borderRadius: 4 }} />
              </div>
              <div style={{ marginBottom: 12 }}>
                <label>Sort Order</label>
                <input type='number' value={formData.sort_order || 0} onChange={(e) => setFormData({...formData, sort_order: parseInt(e.target.value)})} style={{ width: '100%', padding: 8, border: '1px solid #d1d5db', borderRadius: 4 }} />
              </div>
              <div style={{ marginBottom: 12 }}>
                <label><input type='checkbox' checked={formData.is_active !== false} onChange={(e) => setFormData({...formData, is_active: e.target.checked})} /> Active</label>
              </div>
              <div style={{ display: 'flex', gap: 8, justifyContent: 'flex-end' }}>
                <button type='button' onClick={() => { setModalVisible(false); setEditingCategory(null) }} style={{ padding: '8px 16px', border: '1px solid #d1d5db', borderRadius: 4, background: 'white', cursor: 'pointer' }}>Cancel</button>
                <button type='submit' style={{ padding: '8px 16px', background: '#4f46e5', color: 'white', border: 'none', borderRadius: 4, cursor: 'pointer' }}>Save</button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  )
}
