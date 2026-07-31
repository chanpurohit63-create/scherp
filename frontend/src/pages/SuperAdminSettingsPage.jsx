import React, { useState, useEffect } from 'react'
import SuperAdminLayout from '../components/SuperAdminLayout'
import { useAuth } from '../hooks/useAuth.jsx'
import { getResource, updateResource, BACKEND_URL } from '../api'
import toast from 'react-hot-toast'

export default function SuperAdminSettingsPage() {
  const auth = useAuth()
  const [profileForm, setProfileForm] = useState({ full_name: auth.profile?.full_name || '' })
  const [passwordForm, setPasswordForm] = useState({ old_password: '', new_password: '', confirm_password: '' })
  const [loading, setLoading] = useState(false)

  const handleUpdateProfile = async (e) => {
    e.preventDefault()
    setLoading(true)
    try {
      await updateResource(auth.token, 'profile', '', { full_name: profileForm.full_name })
      auth.setProfile({ ...auth.profile, full_name: profileForm.full_name })
      toast.success('Profile updated!')
    } catch (err) {
      toast.error(err.message)
    } finally {
      setLoading(false)
    }
  }

  const handleChangePassword = async (e) => {
    e.preventDefault()
    if (passwordForm.new_password !== passwordForm.confirm_password) {
      toast.error('Passwords do not match')
      return
    }
    setLoading(true)
    try {
      const response = await fetch(`${BACKEND_URL}/api/profile/change-password?old_password=${encodeURIComponent(passwordForm.old_password)}&new_password=${encodeURIComponent(passwordForm.new_password)}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${auth.token}` },
      })
      if (!response.ok) throw new Error((await response.text()) || 'Failed to change password')
      toast.success('Password changed!')
      setPasswordForm({ old_password: '', new_password: '', confirm_password: '' })
    } catch (err) {
      toast.error(err.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <SuperAdminLayout title="Settings" breadcrumbs={[{ label: 'Settings', to: null }]}>
      <div className="settings-grid">
        {/* Platform Info */}
        <section className="card">
          <div className="card-header">
            <h2>Platform Information</h2>
          </div>
          <div className="form-grid">
            <div className="form-group">
              <label>Platform Name</label>
              <div style={{ padding: '10px 14px', background: '#f8fafc', borderRadius: 8, fontWeight: 600 }}>School ERP Platform</div>
            </div>
            <div className="form-group">
              <label>Version</label>
              <div style={{ padding: '10px 14px', background: '#f8fafc', borderRadius: 8 }}>v1.0.0</div>
            </div>
            <div className="form-group">
              <label>Environment</label>
              <div style={{ padding: '10px 14px', background: '#f8fafc', borderRadius: 8 }}><span className="badge badge-success">Production</span></div>
            </div>
            <div className="form-group">
              <label>Admin Email</label>
              <div style={{ padding: '10px 14px', background: '#f8fafc', borderRadius: 8 }}>{auth.profile?.email}</div>
            </div>
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
              <button className="btn btn-primary" type="submit" disabled={loading}>Update Profile</button>
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
              <button className="btn btn-primary" type="submit" disabled={loading}>Change Password</button>
            </div>
          </form>
        </section>
      </div>
    </SuperAdminLayout>
  )
}