import React, { useState, useEffect } from 'react'
import { useAuth } from '../hooks/useAuth'
import { listResources, updateResource } from '../api'
import toast from 'react-hot-toast'

const CATEGORIES = [
  'Academic', 'Homework', 'Attendance', 'Examinations', 'Fees',
  'Payments', 'Messages', 'Events', 'Certificates', 'Documents',
  'Security', 'System', 'Announcements',
]

export default function NotificationSettings() {
  const { token } = useAuth()
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)
  const [prefs, setPrefs] = useState({
    email_enabled: true,
    in_app_enabled: true,
    sound_enabled: true,
    browser_enabled: true,
    quiet_hours_start: '',
    quiet_hours_end: '',
    category_preferences: null,
  })
  const [enabledCategories, setEnabledCategories] = useState(CATEGORIES)

  useEffect(() => {
    fetchPreferences()
  }, [])

  const fetchPreferences = async () => {
    try {
      const data = await listResources(token, 'notifications/preferences', '')
      setPrefs(data)
      if (data.category_preferences) {
        try {
          const cats = JSON.parse(data.category_preferences)
          setEnabledCategories(cats)
        } catch (e) {
          setEnabledCategories(CATEGORIES)
        }
      }
    } catch (e) {
      console.error('Failed to fetch preferences:', e)
    } finally {
      setLoading(false)
    }
  }

  const handleToggleCategory = (category) => {
    setEnabledCategories(prev => {
      if (prev.includes(category)) {
        return prev.filter(c => c !== category)
      }
      return [...prev, category]
    })
  }

  const handleSave = async () => {
    setSaving(true)
    try {
      const payload = {
        ...prefs,
        category_preferences: JSON.stringify(enabledCategories),
      }
      await updateResource(token, 'notifications/preferences', '', payload)
      toast.success('Notification preferences saved')
    } catch (e) {
      toast.error('Failed to save preferences')
    } finally {
      setSaving(false)
    }
  }

  if (loading) {
    return (
      <div className="page-wrapper">
        <div className="loading-skeleton">
          <div className="skeleton-line" style={{ width: '40%' }}></div>
          <div className="skeleton-line" style={{ width: '60%' }}></div>
          <div className="skeleton-line" style={{ width: '80%' }}></div>
        </div>
      </div>
    )
  }

  return (
    <div className="page-wrapper">
      <div className="page-header">
        <h1>Notification Settings</h1>
        <p className="page-subtitle">Configure how you receive notifications</p>
      </div>

      <div className="settings-section">
        <h2>Notification Channels</h2>
        <div className="settings-grid">
          {/* In-App */}
          <label className="setting-item">
            <div className="setting-info">
              <span className="setting-label">In-App Notifications</span>
              <span className="setting-desc">Show notifications within the app</span>
            </div>
            <input
              type="checkbox"
              checked={prefs.in_app_enabled}
              onChange={(e) => setPrefs(prev => ({ ...prev, in_app_enabled: e.target.checked }))}
              className="toggle"
            />
          </label>

          {/* Email */}
          <label className="setting-item">
            <div className="setting-info">
              <span className="setting-label">Email Notifications</span>
              <span className="setting-desc">Receive notifications via email</span>
            </div>
            <input
              type="checkbox"
              checked={prefs.email_enabled}
              onChange={(e) => setPrefs(prev => ({ ...prev, email_enabled: e.target.checked }))}
              className="toggle"
            />
          </label>

          {/* Sound */}
          <label className="setting-item">
            <div className="setting-info">
              <span className="setting-label">Sound Alerts</span>
              <span className="setting-desc">Play sound for new notifications</span>
            </div>
            <input
              type="checkbox"
              checked={prefs.sound_enabled}
              onChange={(e) => setPrefs(prev => ({ ...prev, sound_enabled: e.target.checked }))}
              className="toggle"
            />
          </label>

          {/* Browser */}
          <label className="setting-item">
            <div className="setting-info">
              <span className="setting-label">Desktop Browser Notifications</span>
              <span className="setting-desc">Show browser native notifications</span>
            </div>
            <input
              type="checkbox"
              checked={prefs.browser_enabled}
              onChange={(e) => setPrefs(prev => ({ ...prev, browser_enabled: e.target.checked }))}
              className="toggle"
            />
          </label>
        </div>
      </div>

      <div className="settings-section">
        <h2>Quiet Hours</h2>
        <p className="setting-desc">Mute notifications during specific hours</p>
        <div className="quiet-hours-row">
          <div className="form-group">
            <label>Start Time</label>
            <input
              type="time"
              value={prefs.quiet_hours_start || ''}
              onChange={(e) => setPrefs(prev => ({ ...prev, quiet_hours_start: e.target.value }))}
              className="form-input"
            />
          </div>
          <div className="form-group">
            <label>End Time</label>
            <input
              type="time"
              value={prefs.quiet_hours_end || ''}
              onChange={(e) => setPrefs(prev => ({ ...prev, quiet_hours_end: e.target.value }))}
              className="form-input"
            />
          </div>
        </div>
      </div>

      <div className="settings-section">
        <h2>Category Preferences</h2>
        <p className="setting-desc">Enable or disable notification categories</p>
        <div className="category-grid">
          {CATEGORIES.map(category => (
            <label key={category} className="category-checkbox">
              <input
                type="checkbox"
                checked={enabledCategories.includes(category)}
                onChange={() => handleToggleCategory(category)}
              />
              <span>{category}</span>
            </label>
          ))}
        </div>
      </div>

      <div className="settings-actions">
        <button
          className="btn btn-primary"
          onClick={handleSave}
          disabled={saving}
        >
          {saving ? 'Saving...' : 'Save Preferences'}
        </button>
      </div>
    </div>
  )
}
