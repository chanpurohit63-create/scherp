import React, { useState } from 'react'
import ParentLayout from '../components/ParentLayout'
import { useAuth } from '../hooks/useAuth.jsx'
import { updateResource } from '../api'
import toast from 'react-hot-toast'

export default function ParentChangePasswordPage() {
  const auth = useAuth()
  const [currentPassword, setCurrentPassword] = useState('')
  const [newPassword, setNewPassword] = useState('')
  const [confirmPassword, setConfirmPassword] = useState('')
  const [saving, setSaving] = useState(false)

  const handleSubmit = async (e) => {
    e.preventDefault()
    if (!currentPassword || !newPassword || !confirmPassword) {
      toast.error('All fields are required')
      return
    }
    if (newPassword !== confirmPassword) {
      toast.error('New passwords do not match')
      return
    }
    if (newPassword.length < 6) {
      toast.error('Password must be at least 6 characters')
      return
    }
    setSaving(true)
    try {
      await updateResource(auth.token, 'portal/parent/change-password', 0, {
        current_password: currentPassword,
        new_password: newPassword,
      })
      toast.success('Password changed successfully')
      setCurrentPassword('')
      setNewPassword('')
      setConfirmPassword('')
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Failed to change password')
    } finally {
      setSaving(false)
    }
  }

  return (
    <ParentLayout title="Change Password" hideChildSwitcher>
      <div className="card" style={{ maxWidth: 450 }}>
        <h3>🔑 Change Password</h3>
        <form onSubmit={handleSubmit}>
          <div className="form-grid">
            <label>
              Current Password
              <input className="input" type="password" value={currentPassword} onChange={(e) => setCurrentPassword(e.target.value)} required />
            </label>
            <label>
              New Password
              <input className="input" type="password" value={newPassword} onChange={(e) => setNewPassword(e.target.value)} required minLength={6} />
            </label>
            <label>
              Confirm New Password
              <input className="input" type="password" value={confirmPassword} onChange={(e) => setConfirmPassword(e.target.value)} required minLength={6} />
            </label>
          </div>
          <div className="form-actions" style={{ marginTop: 16 }}>
            <button className="btn btn-primary" type="submit" disabled={saving}>
              {saving ? 'Changing...' : 'Change Password'}
            </button>
          </div>
        </form>
      </div>
    </ParentLayout>
  )
}