import React, { useEffect, useState } from 'react'
import TeacherLayout from '../components/TeacherLayout'
import { useAuth } from '../hooks/useAuth.jsx'
import { listResources, updateResource as updateApi } from '../api'
import toast from 'react-hot-toast'

export default function TeacherProfilePage() {
  const auth = useAuth()
  const [profile, setProfile] = useState(null)
  const [form, setForm] = useState({ full_name: '' })
  const [passwordForm, setPasswordForm] = useState({ current_password: '', new_password: '' })
  const [loading, setLoading] = useState(true)

  useEffect(() => { loadProfile() }, [])

  const loadProfile = async () => {
    try {
      const d = await listResources(auth.token, 'portal/teacher/profile')
      setProfile(d)
      setForm({ full_name: d?.full_name || '' })
    } catch (err) { console.error(err) }
    finally { setLoading(false) }
  }

  const handleUpdate = async () => {
    try {
      await updateApi(auth.token, 'portal/teacher/profile', 0, { full_name: form.full_name })
      auth.setProfile({ ...auth.profile, full_name: form.full_name })
      toast.success('Profile updated')
    } catch (err) { toast.error('Update failed') }
  }

  const handleChangePassword = async () => {
    if (!passwordForm.current_password || !passwordForm.new_password) {
      toast.error('Fill all password fields'); return
    }
    try {
      await updateApi(auth.token, 'portal/teacher/change-password', 0, passwordForm)
      toast.success('Password changed')
      setPasswordForm({ current_password: '', new_password: '' })
    } catch (err) { toast.error('Password change failed') }
  }

  if (loading) {
    return <TeacherLayout title="Profile"><div className="skeleton-card" style={{ height: 200 }} /></TeacherLayout>
  }

  return (
    <TeacherLayout title="My Profile">
      <div className="charts-grid">
        <div className="card">
          <h3>Profile Information</h3>
          <div className="form-grid">
            <label>Email <input className="input" value={profile?.email || ''} readOnly /></label>
            <label>Employee No <input className="input" value={profile?.employee_no || ''} readOnly /></label>
            <label>Full Name <input className="input" value={form.full_name} onChange={(e) => setForm({ ...form, full_name: e.target.value })} /></label>
          </div>
          <div className="form-actions" style={{ marginTop: 12 }}>
            <button className="btn btn-primary" onClick={handleUpdate}>Update Profile</button>
          </div>
        </div>

        <div className="card">
          <h3>Change Password</h3>
          <div className="form-grid">
            <label>Current Password <input className="input" type="password" value={passwordForm.current_password} onChange={(e) => setPasswordForm({ ...passwordForm, current_password: e.target.value })} /></label>
            <label>New Password <input className="input" type="password" value={passwordForm.new_password} onChange={(e) => setPasswordForm({ ...passwordForm, new_password: e.target.value })} /></label>
          </div>
          <div className="form-actions" style={{ marginTop: 12 }}>
            <button className="btn btn-primary" onClick={handleChangePassword}>Change Password</button>
          </div>
        </div>
      </div>
    </TeacherLayout>
  )
}

