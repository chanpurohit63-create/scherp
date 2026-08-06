import React, { useEffect, useState } from 'react'
import SchoolAdminLayout from '../components/SchoolAdminLayout'
import { useAuth } from '../hooks/useAuth.jsx'
import { getResource, updateResource, uploadFile, listResources, BACKEND_URL } from '../api'
import toast from 'react-hot-toast'

export default function SettingsPage() {
  const auth = useAuth()
  const [settings, setSettings] = useState({
    school_name: '', address: '', phone: '', email: '', logo_path: '',
    principal_name: '', theme_color: '#4f46e5', stamp_path: '', signature_path: '',
    academic_year_id: ''
  })
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
      setSettings({
        school_name: data.school_name || '',
        address: data.address || '',
        phone: data.phone || '',
        email: data.email || '',
        logo_path: data.logo_path || '',
        principal_name: data.principal_name || '',
        theme_color: data.theme_color || '#4f46e5',
        stamp_path: data.stamp_path || '',
        signature_path: data.signature_path || '',
        academic_year_id: data.academic_year_id || ''
      })
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
      // Save ALL settings to the database (not localStorage)
      await updateResource(auth.token, 'settings', '', {
        school_name: settings.school_name,
        address: settings.address,
        phone: settings.phone,
        email: settings.email,
        principal_name: settings.principal_name,
        theme_color: settings.theme_color,
        stamp_path: settings.stamp_path,
        signature_path: settings.signature_path,
        logo_path: settings.logo_path,
        academic_year_id: settings.academic_year_id ? Number(settings.academic_year_id) : undefined,
      })
      // Apply theme color immediately
      document.documentElement.style.setProperty('--primary-color', settings.theme_color)
      localStorage.setItem('theme-color', settings.theme_color)
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
      // Fallback: store as base64
      const reader = new FileReader()
      reader.onload = () => {
        setSettings((prev) => ({ ...prev, logo_path: reader.result }))
        toast.success('Logo saved!', { id: toastId })
      }
      reader.readAsDataURL(file)
    }
  }

  const handleStampUpload = async (e) => {
    const file = e.target.files[0]
    if (!file) return
    const toastId = toast.loading('Uploading stamp...')
    try {
      const result = await uploadFile(auth.token, 'settings/stamp', file)
      setSettings((prev) => ({ ...prev, stamp_path: result.stamp_path || result.logo_path || '' }))
      toast.success('Stamp uploaded!', { id: toastId })
    } catch (err) {
      // Fallback: store as base64
      const reader = new FileReader()
      reader.onload = () => {
        setSettings((prev) => ({ ...prev, stamp_path: reader.result }))
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
      setSettings((prev) => ({ ...prev, signature_path: result.signature_path || result.logo_path || '' }))
      toast.success('Signature uploaded!', { id: toastId })
    } catch (err) {
      // Fallback: store as base64
      const reader = new FileReader()
      reader.onload = () => {
        setSettings((prev) => ({ ...prev, signature_path: reader.result }))
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

  const resolveAssetUrl = (path) => {
    if (!path) return null
    if (path.startsWith('data:')) return path
    // If path already starts with /static/, use it directly
    if (path.startsWith('/static/') || path.startsWith('static/')) {
      const cleanPath = path.startsWith('/') ? path : `/${path}`
      return `${BACKEND_URL}${cleanPath}`
    }
    // Otherwise construct path from school_id and filename
    const filename = path.split(/[\\/]/).pop()
    return `${BACKEND_URL}/static/uploads/school_${auth.profile?.school_id || ''}/${filename}`
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
                <input className="input" value={settings.principal_name} onChange={(e) => setSettings({ ...settings, principal_name: e.target.value })} />
              </div>
              <div className="form-group">
                <label>Theme Color</label>
                <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
                  <input type="color" value={settings.theme_color} onChange={(e) => setSettings({ ...settings, theme_color: e.target.value })} style={{ width: 50, height: 40, border: 'none', borderRadius: 8, cursor: 'pointer' }} />
                  <input className="input" value={settings.theme_color} onChange={(e) => setSettings({ ...settings, theme_color: e.target.value })} style={{ flex: 1 }} />
                </div>
              </div>
              <div className="form-group" style={{ gridColumn: 'span 2' }}>
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
            <div className="form-group">
              <label>School Logo</label>
              {(settings.logo_path) && <img src={resolveAssetUrl(settings.logo_path)} alt="Logo" style={{ maxWidth: 150, marginBottom: 8, borderRadius: 8 }} />}
              <input type="file" accept="image/*" onChange={handleLogoUpload} className="input" />
            </div>
            <div className="form-group">
              <label>School Stamp</label>
              {settings.stamp_path && <img src={resolveAssetUrl(settings.stamp_path)} alt="Stamp" style={{ maxWidth: 150, marginBottom: 8, borderRadius: 8 }} />}
              <input type="file" accept="image/*" onChange={handleStampUpload} className="input" />
            </div>
            <div className="form-group" style={{ gridColumn: 'span 2' }}>
              <label>Principal Signature</label>
              {settings.signature_path && <img src={resolveAssetUrl(settings.signature_path)} alt="Signature" style={{ maxWidth: 200, marginBottom: 8, borderRadius: 8 }} />}
              <input type="file" accept="image/*" onChange={handleSignatureUpload} className="input" />
            </div>
          </div>
          <div className="form-actions">
            <button className="btn btn-primary" onClick={handleSaveSettings}>Save Branding</button>
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