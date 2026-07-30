import React, { useEffect, useState } from 'react'
import PageWrapper from '../components/PageWrapper'
import { useAuth } from '../hooks/useAuth.jsx'
import { listResources, getBackendUrl } from '../api'

const DAY_NAMES = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']

export default function TeacherAvailabilityPage() {
  const auth = useAuth()
  const [availability, setAvailability] = useState([])
  const [loading, setLoading] = useState(true)
  const [teacherId, setTeacherId] = useState('')
  const [showForm, setShowForm] = useState(false)
  const [formData, setFormData] = useState({
    teacher_id: '',
    day_of_week: 0,
    period_number: 1,
    is_available: true,
    availability_type: 'available',
  })

  useEffect(() => {
    loadAvailability()
  }, [])

  const loadAvailability = async () => {
    try {
      const tid = teacherId || auth.profile?.id
      const data = await listResources(auth.token, `teachers/${tid}/availability`)
      setAvailability(data)
    } catch (err) {
      console.error(err)
    } finally {
      setLoading(false)
    }
  }

  const handleCreate = async (e) => {
    e.preventDefault()
    try {
      const response = await fetch(`${getBackendUrl()}/api/teachers/${formData.teacher_id}/availability`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${auth.token}` },
        body: JSON.stringify([formData]),
      })
      if (response.ok) {
        setShowForm(false)
        setFormData({ teacher_id: '', day_of_week: 0, period_number: 1, is_available: true, availability_type: 'available' })
        loadAvailability()
      }
    } catch (err) {
      console.error(err)
    }
  }

  if (loading) {
    return (
      <PageWrapper title="Teacher Availability">
        <div className="skeleton-grid">
          {Array.from({ length: 4 }).map((_, i) => <div key={i} className="skeleton-card" />)}
        </div>
      </PageWrapper>
    )
  }

  return (
    <PageWrapper title="Teacher Availability">
      <div className="flex gap-4 mb-6">
        <div className="form-group">
          <label>Teacher ID</label>
          <input type="number" value={teacherId} onChange={(e) => setTeacherId(e.target.value)} className="input" />
        </div>
        <button onClick={loadAvailability} className="btn btn-primary">Load</button>
        <button onClick={() => setShowForm(!showForm)} className="btn btn-secondary">
          {showForm ? 'Cancel' : 'Add Availability'}
        </button>
      </div>

      {showForm && (
        <form onSubmit={handleCreate} className="card mb-6">
          <h3 className="card-title">Set Availability</h3>
          <div className="form-group">
            <label>Teacher ID</label>
            <input type="number" name="teacher_id" value={formData.teacher_id} onChange={(e) => setFormData({ ...formData, teacher_id: e.target.value })} className="input" required />
          </div>
          <div className="form-group">
            <label>Day</label>
            <select name="day_of_week" value={formData.day_of_week} onChange={(e) => setFormData({ ...formData, day_of_week: parseInt(e.target.value) })} className="input">
              {DAY_NAMES.map((d, i) => <option key={i} value={i}>{d}</option>)}
            </select>
          </div>
          <div className="form-group">
            <label>Period</label>
            <input type="number" name="period_number" value={formData.period_number} onChange={(e) => setFormData({ ...formData, period_number: parseInt(e.target.value) })} className="input" min={1} />
          </div>
          <div className="form-group">
            <label>Available</label>
            <input type="checkbox" name="is_available" checked={formData.is_available} onChange={(e) => setFormData({ ...formData, is_available: e.target.checked })} />
          </div>
          <div className="form-group">
            <label>Type</label>
            <select name="availability_type" value={formData.availability_type} onChange={(e) => setFormData({ ...formData, availability_type: e.target.value })} className="input">
              <option value="available">Available</option>
              <option value="unavailable">Unavailable</option>
              <option value="leave">On Leave</option>
              <option value="preferred">Preferred</option>
            </select>
          </div>
          <button type="submit" className="btn btn-primary">Save</button>
        </form>
      )}

      <div className="card">
        <h3 className="card-title">Availability Records</h3>
        <div className="table-responsive">
          <table className="table">
            <thead>
              <tr>
                <th>Day</th>
                <th>Period</th>
                <th>Available</th>
                <th>Type</th>
              </tr>
            </thead>
            <tbody>
              {availability.map((a) => (
                <tr key={a.id}>
                  <td>{DAY_NAMES[a.day_of_week]}</td>
                  <td>{a.period_number}</td>
                  <td>{a.is_available ? 'Yes' : 'No'}</td>
                  <td><span className="badge badge-info">{a.availability_type}</span></td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </PageWrapper>
  )
}