import React, { useEffect, useState } from 'react'
import SchoolAdminLayout from '../components/SchoolAdminLayout'
import { useAuth } from '../hooks/useAuth.jsx'
import { getResource, updateResource, uploadFile, listResources, BACKEND_URL } from '../api'
import toast from 'react-hot-toast'

export default function SettingsPage() {
  const auth = useAuth()
  const [settings, setSettings] = useState({ school_name: '', address: '', phone: '', email: '', logo_path: '', academic_year_id: '' })
  const [academicYears, setAcademicYears] = useState([])
  const [profileForm, setProfileForm] = useState({ full_name: auth.profile?.full_name || '' })
  const [passwordForm, setPasswordForm] = useState({ old_password: '', new_password: '', confirm_password: '' })
  const [loading, setLoading] = useState(false)
  const [localSettings, setLocalSettings] = useState({ principal_name: '', theme_color: '#4f46e5', stamp_path: '', signature_path: '' })

  useEffect(() => {
    loadSettings()
    loadAcademicYears()
    loadLocalSettings()
  }, [])

  const loadSettings = async () => {
    try {
      const data = await getResource(auth.token, 'settings', '')
      setSettings({ school_name: data.school_name || '', address: data.address || '', phone: data.phone || '', email: data.email || '', logo_path: data.logo_path || '', academic_year_id: data.academic_year_id || '' })
    } catch (err) {
      // silent
    }
  }

  const loadAcademicYears = async () => {
    try {
      const data = await listResources(auth.token, 'academic-years')
      setAcademicYears(data)
    } catch (err) {
      // silent
    }
  }

  const loadLocalSettings = () => {
    const stored = localStorage.getItem('school-local-settings')
    if (stored) {
      setLocalSettings(JSON.parse(stored))
    }
  }

  const saveLocalSettings = (newSettings) => {
    localStorage.setItem('school-local-settings', JSON.stringify(newSettings))
    setLocalSettings(newSettings)
  }

  const handleSaveSettings = async (e) => {
    e.preventDefault()
    const toastId = toast.loading('Saving settings...')
    try {
      await updateResource(auth.token, 'settings', '', settings)
      saveLocalSettings(localSettings)
      toast.success('Settings saved!', { id: toastId })
    } catch (err) {
      toast.error(err.message, { id: toastId })
    }
  }

  const handleLogoUpload = async (e) => {
    const file = e.target.files[0]
    if (!file) return
    const toastId = toast.loading('Uploading logo...')
    try {
      const result = await uploadFile(auth.token, 'settings/logo', file)
      setSettings((prev) => ({ ...prev, logo_path: result.logo_path }))
      toast.success('Logo uploaded!', { id: toastId })
    } catch (err) {
      toast.error(err.message, { id: toastId })
    }
  }

  const handleStampUpload = async (e) => {
    const file = e.target.files[0]
    if (!file) return
    const toastId = toast.loading('Uploading stamp...')
    try {
      const result = await uploadFile(auth.token, 'settings/stamp', file)
      setLocalSettings((prev) => {
        const updated = { ...prev, stamp_path: result.logo_path || result.path || '' }
        saveLocalSettings(updated)
        return updated
      })
      toast.success('Stamp uploaded!', { id: toastId })
    } catch (err) {
      // Fallback: store as base64 in localStorage
      const reader = new FileReader()
      reader.onload = () => {
        const updated = { ...localSettings, stamp_path: reader.result }
        saveLocalSettings(updated)
        setLocalSettings(updated)
        toast.success('Stamp saved!', { id: toastId })
      }
      reader.readAsDataURL(file)
    }
  }

  const handleSignatureUpload = async (e) => {
    const file = e.target.files[0]
    if (!file) return
    const toastId = toast.loading('Uploading signature...')
    try {
      const result = await uploadFile(auth.token, 'settings/signature', file)
      setLocalSettings((prev) => {
        const updated = { ...prev, signature_path: result.logo_path || result.path || '' }
        saveLocalSettings(updated)
        return updated
      })
      toast.success('Signature uploaded!', { id: toastId })
    } catch (err) {
      // Fallback: store as base64 in localStorage
      const reader = new FileReader()
      reader.onload = () => {
        const updated = { ...localSettings, signature_path: reader.result }
        saveLocalSettings(updated)
        setLocalSettings(updated)
        toast.success('Signature saved!', { id: toastId })
      }
      reader.readAsDataURL(file)
    }
  }

  const handleUpdateProfile = async (e) => {
    e.preventDefault()
    try {
      await updateResource(auth.token, 'profile', '', { full_name: profileForm.full_name })
      auth.setProfile({ ...auth.profile, full_name: profileForm.full_name })
      toast.success('Profile updated!')
    } catch (err) {
      toast.error(err.message)
    }
  }

  const handleChangePassword = async (e) => {
    e.preventDefault()
    if (passwordForm.new_password !== passwordForm.confirm_password) {
      toast.error('Passwords do not match')
      return
    }
    const toastId = toast.loading('Changing password...')
    try {
      const response = await fetch(`${BACKEND_URL}/api/profile/change-password?old_password=${encodeURIComponent(passwordForm.old_password)}&new_password=${encodeURIComponent(passwordForm.new_password)}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${auth.token}` },
      })
      if (!response.ok) throw new Error((await response.text()) || 'Failed to change password')
      toast.success('Password changed!', { id: toastId })
      setPasswordForm({ old_password: '', new_password: '', confirm_password: '' })
    } catch (err) {
      toast.error(err.message, { id: toastId })
    }
  }

  return (
    <SchoolAdminLayout title="Organization Settings" breadcrumbs={[{ label: 'Settings', to: null }]}>
      <div className="settings-grid">
        {/* School Profile */}
        <section className="card">
          <div className="card-header">
            <h2>School Profile</h2>
          </div>
          <form onSubmit={handleSaveSettings}>
            <div className="form-grid">
              <div className="form-group" style={{ gridColumn: 'span 2' }}>
                <label>School Name</label>
                <input className="input" value={settings.school_name} onChange={(e) => setSettings({ ...settings, school_name: e.target.value })} />
              </div>
              <div className="form-group" style={{ gridColumn: 'span 2' }}>
                <label>Address</label>
                <textarea className="input" value={settings.address} onChange={(e) => setSettings({ ...settings, address: e.target.value })} />
              </div>
              <div className="form-group">
                <label>Phone</label>
                <input className="input" value={settings.phone} onChange={(e) => setSettings({ ...settings, phone: e.target.value })} />
              </div>
              <div className="form-group">
                <label>Email</label>
                <input className="input" type="email" value={settings.email} onChange={(e) => setSettings({ ...settings, email: e.target.value })} />
              </div>
              <div className="form-group">
                <label>Principal Name</label>
                <input className="input" value={localSettings.principal_name} onChange={(e) => setLocalSettings({ ...localSettings, principal_name: e.target.value })} />
              </div>
              <div className="form-group">
                <label>Active Academic Year</label>
                <select className="input" value={settings.academic_year_id} onChange={(e) => setSettings({ ...settings, academic_year_id: e.target.value })}>
                  <option value="">None</option>
                  {academicYears.map((y) => <option key={y.id} value={y.id}>{y.name}</option>)}
                </select>
              </div>
            </div>
            <div className="form-actions">
              <button className="btn btn-primary" type="submit">Save Settings</button>
            </div>
          </form>
        </section>

        {/* Branding */}
        <section className="card">
          <div className="card-header">
            <h2>Branding & Assets</h2>
          </div>
          <div className="form-grid">
            <div className="form-group" style={{ gridColumn: 'span 2' }}>
              <label>Theme Color</label>
              <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
                <input type="color" value={localSettings.theme_color} onChange={(e) => setLocalSettings({ ...localSettings, theme_color: e.target.value })} style={{ width: 50, height: 40, border: 'none', borderRadius: 8, cursor: 'pointer' }} />
                <input className="input" value={localSettings.theme_color} onChange={(e) => setLocalSettings({ ...localSettings, theme_color: e.target.value })} style={{ flex: 1 }} />
              </div>
            </div>
            <div className="form-group">
              <label>School Logo</label>
              {settings.logo_path && <img src={`${BACKEND_URL}/static/uploads/${settings.logo_path.split('/').pop()}`} alt="Logo" style={{ maxWidth: 150, marginBottom: 8, borderRadius: 8 }} />}
              <input type="file" accept="image/*" onChange={handleLogoUpload} className="input" />
            </div>
            <div className="form-group">
              <label>School Stamp</label>
              {localSettings.stamp_path && <img src={localSettings.stamp_path.startsWith('data:') ? localSettings.stamp_path : `${BACKEND_URL}/static/uploads/${localSettings.stamp_path.split('/').pop()}`} alt="Stamp" style={{ maxWidth: 150, marginBottom: 8, borderRadius: 8 }} />}
              <input type="file" accept="image/*" onChange={handleStampUpload} className="input" />
            </div>
            <div className="form-group" style={{ gridColumn: 'span 2' }}>
              <label>Principal Signature</label>
              {localSettings.signature_path && <img src={localSettings.signature_path.startsWith('data:') ? localSettings.signature_path : `${BACKEND_URL}/static/uploads/${localSettings.signature_path.split('/').pop()}`} alt="Signature" style={{ maxWidth: 200, marginBottom: 8, borderRadius: 8 }} />}
              <input type="file" accept="image/*" onChange={handleSignatureUpload} className="input" />
            </div>
          </div>
          <div className="form-actions">
            <button className="btn btn-primary" onClick={(e) => { e.preventDefault(); saveLocalSettings(localSettings); toast.success('Branding saved!') }}>Save Branding</button>
          </div>
        </section>

        {/* Update Profile */}
        <section className="card">
          <div className="card-header">
            <h2>Update Profile</h2>
          </div>
          <form onSubmit={handleUpdateProfile}>
            <div className="form-group">
              <label>Full Name</label>
              <input className="input" value={profileForm.full_name} onChange={(e) => setProfileForm({ full_name: e.target.value })} />
            </div>
            <div className="form-actions">
              <button className="btn btn-primary" type="submit">Update Profile</button>
            </div>
          </form>
        </section>

        {/* Change Password */}
        <section className="card">
          <div className="card-header">
            <h2>Change Password</h2>
          </div>
          <form onSubmit={handleChangePassword}>
            <div className="form-group">
              <label>Current Password</label>
              <input className="input" type="password" value={passwordForm.old_password} onChange={(e) => setPasswordForm({ ...passwordForm, old_password: e.target.value })} required />
            </div>
            <div className="form-group">
              <label>New Password</label>
              <input className="input" type="password" value={passwordForm.new_password} onChange={(e) => setPasswordForm({ ...passwordForm, new_password: e.target.value })} required />
            </div>
            <div className="form-group">
              <label>Confirm Password</label>
              <input className="input" type="password" value={passwordForm.confirm_password} onChange={(e) => setPasswordForm({ ...passwordForm, confirm_password: e.target.value })} required />
            </div>
            <div className="form-actions">
              <button className="btn btn-primary" type="submit">Change Password</button>
            </div>
          </form>
        </section>
      </div>
    </SchoolAdminLayout>
  )
}