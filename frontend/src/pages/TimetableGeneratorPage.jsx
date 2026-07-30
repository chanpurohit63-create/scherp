import React, { useEffect, useState } from 'react'
import PageWrapper from '../components/PageWrapper'
import { useAuth } from '../hooks/useAuth.jsx'
import { listResources, getBackendUrl } from '../api'

const DAY_NAMES = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']

export default function TimetableGeneratorPage() {
  const auth = useAuth()
  const [result, setResult] = useState(null)
  const [loading, setLoading] = useState(false)
  const [config, setConfig] = useState({
    academic_year_id: '',
    working_days: [0, 1, 2, 3, 4, 5],
    school_start_time: '08:00',
    school_end_time: '15:00',
    periods_per_day: 6,
    break_periods: [],
    max_periods_per_day: 6,
    max_periods_per_week: 30,
    auto_assign_teachers: true,
    auto_assign_rooms: true,
    auto_assign_periods: true,
    copy_from_academic_year_id: '',
    copy_from_section_id: '',
    copy_to_section_id: '',
  })

  const handleChange = (e) => {
    const { name, value, type, checked } = e.target
    if (type === 'checkbox') {
      setConfig((prev) => ({ ...prev, [name]: checked }))
    } else {
      setConfig((prev) => ({ ...prev, [name]: value }))
    }
  }

  const handleGenerate = async (e) => {
    e.preventDefault()
    setLoading(true)
    try {
      const response = await fetch(`${getBackendUrl()}/api/timetable/generate`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${auth.token}` },
        body: JSON.stringify(config),
      })
      if (response.ok) {
        const data = await response.json()
        setResult(data)
      } else {
        const err = await response.text()
        alert(`Generation failed: ${err}`)
      }
    } catch (err) {
      console.error(err)
      alert('Generation failed')
    } finally {
      setLoading(false)
    }
  }

  return (
    <PageWrapper title="Timetable Generator">
      <form onSubmit={handleGenerate} className="card">
        <h3 className="card-title">Auto-Generate Timetable</h3>

        <div className="form-group">
          <label>Academic Year ID</label>
          <input type="number" name="academic_year_id" value={config.academic_year_id} onChange={handleChange} className="input" required />
        </div>

        <div className="form-group">
          <label>Periods Per Day</label>
          <input type="number" name="periods_per_day" value={config.periods_per_day} onChange={handleChange} className="input" min={1} max={12} />
        </div>

        <div className="form-group">
          <label>School Start Time</label>
          <input type="time" name="school_start_time" value={config.school_start_time} onChange={handleChange} className="input" />
        </div>

        <div className="form-group">
          <label>School End Time</label>
          <input type="time" name="school_end_time" value={config.school_end_time} onChange={handleChange} className="input" />
        </div>

        <div className="form-group">
          <label>Max Periods Per Day</label>
          <input type="number" name="max_periods_per_day" value={config.max_periods_per_day} onChange={handleChange} className="input" />
        </div>

        <div className="form-group">
          <label>Max Periods Per Week</label>
          <input type="number" name="max_periods_per_week" value={config.max_periods_per_week} onChange={handleChange} className="input" />
        </div>

        <div className="form-group">
          <label>Working Days (0=Mon, 5=Sat)</label>
          <input type="text" name="working_days" value={config.working_days.join(',')} onChange={handleChange} className="input" />
        </div>

        <div className="form-group">
          <label>Break Periods (comma-separated)</label>
          <input type="text" name="break_periods" value={config.break_periods.join(',')} onChange={handleChange} className="input" />
        </div>

        <div className="form-group">
          <label>Copy From Academic Year ID (optional)</label>
          <input type="number" name="copy_from_academic_year_id" value={config.copy_from_academic_year_id} onChange={handleChange} className="input" />
        </div>

        <div className="form-group">
          <label>Copy From Section ID (optional)</label>
          <input type="number" name="copy_from_section_id" value={config.copy_from_section_id} onChange={handleChange} className="input" />
        </div>

        <div className="form-group">
          <label>Copy To Section ID (optional)</label>
          <input type="number" name="copy_to_section_id" value={config.copy_to_section_id} onChange={handleChange} className="input" />
        </div>

        <div className="form-group">
          <label>Auto Assign Teachers</label>
          <input type="checkbox" name="auto_assign_teachers" checked={config.auto_assign_teachers} onChange={handleChange} />
        </div>

        <div className="form-group">
          <label>Auto Assign Rooms</label>
          <input type="checkbox" name="auto_assign_rooms" checked={config.auto_assign_rooms} onChange={handleChange} />
        </div>

        <button type="submit" className="btn btn-primary" disabled={loading}>
          {loading ? 'Generating...' : 'Generate Timetable'}
        </button>
      </form>

      {result && (
        <div className="card mt-6">
          <h3 className="card-title">Generation Result</h3>
          <p><strong>Generated:</strong> {result.generated} entries</p>
          <p><strong>Conflicts Found:</strong> {result.conflicts_found}</p>
          <p><strong>Log ID:</strong> {result.log_id}</p>
        </div>
      )}
    </PageWrapper>
  )
}