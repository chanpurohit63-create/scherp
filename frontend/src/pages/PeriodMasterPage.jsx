import React, { useEffect, useState } from 'react'
import PageWrapper from '../components/PageWrapper'
import { useAuth } from '../hooks/useAuth.jsx'
import { listResources, getBackendUrl } from '../api'

export default function PeriodMasterPage() {
  const auth = useAuth()
  const [periods, setPeriods] = useState([])
  const [loading, setLoading] = useState(true)
  const [showForm, setShowForm] = useState(false)
  const [formData, setFormData] = useState({
    period_name: '',
    period_number: '',
    start_time: '',
    end_time: '',
    is_break: false,
    is_assembly: false,
    is_sports: false,
    is_library: false,
    is_practical: false,
    sort_order: 0,
  })

  useEffect(() => {
    loadPeriods()
  }, [])

  const loadPeriods = async () => {
    try {
      const data = await listResources(auth.token, 'periods')
      setPeriods(data)
    } catch (err) {
      console.error(err)
    } finally {
      setLoading(false)
    }
  }

  const handleCreate = async (e) => {
    e.preventDefault()
    try {
      const response = await fetch(`${getBackendUrl()}/api/periods`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${auth.token}` },
        body: JSON.stringify(formData),
      })
      if (response.ok) {
        setShowForm(false)
        setFormData({ period_name: '', period_number: '', start_time: '', end_time: '', is_break: false, is_assembly: false, is_sports: false, is_library: false, is_practical: false, sort_order: 0 })
        loadPeriods()
      }
    } catch (err) {
      console.error(err)
    }
  }

  const handleDelete = async (periodId) => {
    if (!window.confirm('Delete this period?')) return
    try {
      const response = await fetch(`${getBackendUrl()}/api/periods/${periodId}`, {
        method: 'DELETE',
        headers: { Authorization: `Bearer ${auth.token}` },
      })
      if (response.ok) {
        loadPeriods()
      }
    } catch (err) {
      console.error(err)
    }
  }

  if (loading) {
    return (
      <PageWrapper title="Period Master">
        <div className="skeleton-grid">
          {Array.from({ length: 4 }).map((_, i) => <div key={i} className="skeleton-card" />)}
        </div>
      </PageWrapper>
    )
  }

  return (
    <PageWrapper title="Period Master">
      <div className="flex gap-4 mb-6">
        <button onClick={() => setShowForm(!showForm)} className="btn btn-primary">
          {showForm ? 'Cancel' : 'Add Period'}
        </button>
      </div>

      {showForm && (
        <form onSubmit={handleCreate} className="card mb-6">
          <h3 className="card-title">Add New Period</h3>
          <div className="form-group">
            <label>Period Name</label>
            <input type="text" name="period_name" value={formData.period_name} onChange={(e) => setFormData({ ...formData, period_name: e.target.value })} className="input" required />
          </div>
          <div className="form-group">
            <label>Period Number</label>
            <input type="number" name="period_number" value={formData.period_number} onChange={(e) => setFormData({ ...formData, period_number: e.target.value })} className="input" required />
          </div>
          <div className="form-group">
            <label>Start Time</label>
            <input type="time" name="start_time" value={formData.start_time} onChange={(e) => setFormData({ ...formData, start_time: e.target.value })} className="input" required />
          </div>
          <div className="form-group">
            <label>End Time</label>
            <input type="time" name="end_time" value={formData.end_time} onChange={(e) => setFormData({ ...formData, end_time: e.target.value })} className="input" required />
          </div>
          <div className="form-group">
            <label>Sort Order</label>
            <input type="number" name="sort_order" value={formData.sort_order} onChange={(e) => setFormData({ ...formData, sort_order: e.target.value })} className="input" />
          </div>
          <button type="submit" className="btn btn-primary">Create Period</button>
        </form>
      )}

      <div className="card">
        <h3 className="card-title">Periods ({periods.length})</h3>
        <div className="table-responsive">
          <table className="table">
            <thead>
              <tr>
                <th>Name</th>
                <th>Number</th>
                <th>Start</th>
                <th>End</th>
                <th>Break</th>
                <th>Assembly</th>
                <th>Sports</th>
                <th>Library</th>
                <th>Practical</th>
                <th>Sort</th>
                <th>Action</th>
              </tr>
            </thead>
            <tbody>
              {periods.map((p) => (
                <tr key={p.id}>
                  <td>{p.period_name}</td>
                  <td>{p.period_number}</td>
                  <td>{p.start_time}</td>
                  <td>{p.end_time}</td>
                  <td>{p.is_break ? 'Yes' : 'No'}</td>
                  <td>{p.is_assembly ? 'Yes' : 'No'}</td>
                  <td>{p.is_sports ? 'Yes' : 'No'}</td>
                  <td>{p.is_library ? 'Yes' : 'No'}</td>
                  <td>{p.is_practical ? 'Yes' : 'No'}</td>
                  <td>{p.sort_order}</td>
                  <td>
                    <button onClick={() => handleDelete(p.id)} className="btn btn-sm btn-danger">Delete</button>
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