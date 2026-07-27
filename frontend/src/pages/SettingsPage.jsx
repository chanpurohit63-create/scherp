import React, { useEffect, useState } from 'react'
import PageWrapper from '../components/PageWrapper'
import { useAuth } from '../hooks/useAuth.jsx'
import { getResource, updateResource, uploadFile, listResources } from '../api'
import toast from 'react-hot-toast'

export default function SettingsPage() {
  const auth = useAuth()
  const [settings, setSettings] = useState({ school_name: '', address: '', phone: '', email: '', logo_path: '', academic_year_id: '' })
  const [academicYears, setAcademicYears] = useState([])
  const [profileForm, setProfileForm] = useState({ full_name: auth.profile?.full_name || '' })
  const [passwordForm, setPasswordForm] = useState({ old_password: '', new_password: '', confirm_password: '' })
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    loadSettings()
    loadAcademicYears()
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

  const handleSaveSettings = async (e) => {
    e.preventDefault()
    const toastId = toast.loading('Saving settings...')
    try {
      await updateResource(auth.token, 'settings', '', settings)
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
      const response = await fetch('http://127.0.0.1:8000/api/profile/change-password', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${auth.token}` },
        body: JSON.stringify({ old_password: passwordForm.old_password, new_password: passwordForm.new_password }),
      })
      if (!response.ok) throw new Error((await response.text()) || 'Failed to change password')
      toast.success('Password changed!', { id: toastId })
      setPasswordForm({ old_password: '', new_password: '', confirm_password: '' })
    } catch (err) {
      toast.error(err.message, { id: toastId })
    }
  }

  return (
    <PageWrapper title="Settings">
      <div className="settings-grid">
        <section className="card">
          <h2>School Profile</h2>
          <form onSubmit={handleSaveSettings} className="form-grid">
            <label>School Name <input className="input" value={settings.school_name} onChange={(e) => setSettings({ ...settings, school_name: e.target.value })} /></label>
            <label>Address <input className="input" value={settings.address} onChange={(e) => setSettings({ ...settings, address: e.target.value })} /></label>
            <label>Phone <input className="input" value={settings.phone} onChange={(e) => setSettings({ ...settings, phone: e.target.value })} /></label>
            <label>Email <input className="input" value={settings.email} onChange={(e) => setSettings({ ...settings, email: e.target.value })} /></label>
            <label>
              Active Academic Year
              <select className="input" value={settings.academic_year_id} onChange={(e) => setSettings({ ...settings, academic_year_id: e.target.value })}>
                <option value="">None</option>
                {academicYears.map((y) => <option key={y.id} value={y.id}>{y.name}</option>)}
              </select>
            </label>
            <div className="form-actions">
              <button className="btn btn-primary" type="submit">Save Settings</button>
            </div>
          </form>
        </section>

        <section className="card">
          <h2>School Logo</h2>
          {settings.logo_path && <img src={`http://127.0.0.1:8000/static/uploads/${settings.logo_path.split('/').pop()}`} alt="Logo" style={{ maxWidth: 200, marginBottom: 12 }} />}
          <input type="file" accept="image/*" onChange={handleLogoUpload} />
        </section>

        <section className="card">
          <h2>Update Profile</h2>
          <form onSubmit={handleUpdateProfile} className="form-grid">
            <label>Full Name <input className="input" value={profileForm.full_name} onChange={(e) => setProfileForm({ full_name: e.target.value })} /></label>
            <button className="btn btn-primary" type="submit">Update Profile</button>
          </form>
        </section>

        <section className="card">
          <h2>Change Password</h2>
          <form onSubmit={handleChangePassword} className="form-grid">
            <label>Current Password <input className="input" type="password" value={passwordForm.old_password} onChange={(e) => setPasswordForm({ ...passwordForm, old_password: e.target.value })} required /></label>
            <label>New Password <input className="input" type="password" value={passwordForm.new_password} onChange={(e) => setPasswordForm({ ...passwordForm, new_password: e.target.value })} required /></label>
            <label>Confirm Password <input className="input" type="password" value={passwordForm.confirm_password} onChange={(e) => setPasswordForm({ ...passwordForm, confirm_password: e.target.value })} required /></label>
            <button className="btn btn-primary" type="submit">Change Password</button>
          </form>
        </section>
      </div>
    </PageWrapper>
  )
}

