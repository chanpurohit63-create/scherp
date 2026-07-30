import React, { useEffect, useState } from 'react'
import PageWrapper from '../components/PageWrapper'
import { useAuth } from '../hooks/useAuth.jsx'
import { listResources, getBackendUrl } from '../api'

const ROOM_TYPES = ['Classroom', 'Lab', 'Computer Lab', 'Library', 'Auditorium', 'Sports Hall']

export default function RoomManagementPage() {
  const auth = useAuth()
  const [rooms, setRooms] = useState([])
  const [loading, setLoading] = useState(true)
  const [showForm, setShowForm] = useState(false)
  const [formData, setFormData] = useState({
    room_name: '',
    room_number: '',
    building: '',
    floor: '',
    capacity: '',
    room_type: 'Classroom',
    color: '#4f46e5',
    is_active: true,
  })

  useEffect(() => {
    loadRooms()
  }, [])

  const loadRooms = async () => {
    try {
      const data = await listResources(auth.token, 'rooms')
      setRooms(data)
    } catch (err) {
      console.error(err)
    } finally {
      setLoading(false)
    }
  }

  const handleCreate = async (e) => {
    e.preventDefault()
    try {
      const payload = {
        ...formData,
        capacity: formData.capacity ? parseInt(formData.capacity) : null,
        floor: formData.floor ? parseInt(formData.floor) : null,
      }
      const response = await fetch(`${getBackendUrl()}/api/rooms`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${auth.token}` },
        body: JSON.stringify(payload),
      })
      if (response.ok) {
        setShowForm(false)
        setFormData({ room_name: '', room_number: '', building: '', floor: '', capacity: '', room_type: 'Classroom', color: '#4f46e5', is_active: true })
        loadRooms()
      }
    } catch (err) {
      console.error(err)
    }
  }

  const handleDelete = async (roomId) => {
    if (!window.confirm('Delete this room?')) return
    try {
      const response = await fetch(`${getBackendUrl()}/api/rooms/${roomId}`, {
        method: 'DELETE',
        headers: { Authorization: `Bearer ${auth.token}` },
      })
      if (response.ok) {
        loadRooms()
      }
    } catch (err) {
      console.error(err)
    }
  }

  if (loading) {
    return (
      <PageWrapper title="Room Management">
        <div className="skeleton-grid">
          {Array.from({ length: 4 }).map((_, i) => <div key={i} className="skeleton-card" />)}
        </div>
      </PageWrapper>
    )
  }

  return (
    <PageWrapper title="Room Management">
      <div className="flex gap-4 mb-6">
        <button onClick={() => setShowForm(!showForm)} className="btn btn-primary">
          {showForm ? 'Cancel' : 'Add Room'}
        </button>
      </div>

      {showForm && (
        <form onSubmit={handleCreate} className="card mb-6">
          <h3 className="card-title">Add New Room</h3>
          <div className="form-group">
            <label>Room Name</label>
            <input type="text" name="room_name" value={formData.room_name} onChange={(e) => setFormData({ ...formData, room_name: e.target.value })} className="input" required />
          </div>
          <div className="form-group">
            <label>Room Number</label>
            <input type="text" name="room_number" value={formData.room_number} onChange={(e) => setFormData({ ...formData, room_number: e.target.value })} className="input" />
          </div>
          <div className="form-group">
            <label>Building</label>
            <input type="text" name="building" value={formData.building} onChange={(e) => setFormData({ ...formData, building: e.target.value })} className="input" />
          </div>
          <div className="form-group">
            <label>Floor</label>
            <input type="number" name="floor" value={formData.floor} onChange={(e) => setFormData({ ...formData, floor: e.target.value })} className="input" />
          </div>
          <div className="form-group">
            <label>Capacity</label>
            <input type="number" name="capacity" value={formData.capacity} onChange={(e) => setFormData({ ...formData, capacity: e.target.value })} className="input" />
          </div>
          <div className="form-group">
            <label>Room Type</label>
            <select name="room_type" value={formData.room_type} onChange={(e) => setFormData({ ...formData, room_type: e.target.value })} className="input">
              {ROOM_TYPES.map((t) => <option key={t} value={t}>{t}</option>)}
            </select>
          </div>
          <div className="form-group">
            <label>Color</label>
            <input type="color" name="color" value={formData.color} onChange={(e) => setFormData({ ...formData, color: e.target.value })} className="input" />
          </div>
          <button type="submit" className="btn btn-primary">Create Room</button>
        </form>
      )}

      <div className="card">
        <h3 className="card-title">Rooms ({rooms.length})</h3>
        <div className="table-responsive">
          <table className="table">
            <thead>
              <tr>
                <th>Name</th>
                <th>Number</th>
                <th>Building</th>
                <th>Floor</th>
                <th>Capacity</th>
                <th>Type</th>
                <th>Active</th>
                <th>Action</th>
              </tr>
            </thead>
            <tbody>
              {rooms.map((r) => (
                <tr key={r.id}>
                  <td>{r.room_name}</td>
                  <td>{r.room_number || '-'}</td>
                  <td>{r.building || '-'}</td>
                  <td>{r.floor || '-'}</td>
                  <td>{r.capacity || '-'}</td>
                  <td><span className="badge badge-info">{r.room_type}</span></td>
                  <td>{r.is_active ? 'Yes' : 'No'}</td>
                  <td>
                    <button onClick={() => handleDelete(r.id)} className="btn btn-sm btn-danger">Delete</button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </PageWrapper>
  )
}