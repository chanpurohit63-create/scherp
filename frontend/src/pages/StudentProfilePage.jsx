import React, { useEffect, useState } from 'react'
import StudentLayout from '../components/StudentLayout'
import { useAuth } from '../hooks/useAuth.jsx'
import { getResource, updateResource, uploadFile, listResources } from '../api'
import toast from 'react-hot-toast'

export default function StudentProfilePage() {
  const auth = useAuth()
  const [profile, setProfile] = useState(null)
  const [loading, setLoading] = useState(true)
  const [editing, setEditing] = useState(false)
  const [fullName, setFullName] = useState('')
  const [curPwd, setCurPwd] = useState('')
  const [newPwd, setNewPwd] = useState('')

  useEffect(() => {
    loadProfile()
  }, [])

  const loadProfile = async () => {
    try {
      const d = await listResources(auth.token, 'portal/student/profile')
      setProfile(d)
      setFullName(d.full_name || '')
    } catch (err) {
      console.error(err)
    } finally {
      setLoading(false)
    }
  }

  const handleUpdate = async () => {
    try {
      await updateResource(auth.token, 'portal/student/profile', '', { full_name: fullName })
      toast.success('Profile updated')
      setEditing(false)
      loadProfile()
    } catch (err) {
      toast.error('Update failed')
    }
  }

  const handlePhoto = async (e) => {
    try {
      await uploadFile(auth.token, 'portal/student/photo', e.target.files[0])
      toast.success('Photo updated')
      loadProfile()
    } catch (err) {
      toast.error('Photo upload failed')
    }
  }

  const handleChangePassword = async () => {
    if (!curPwd || !newPwd) { toast.error('Fill all fields'); return }
    try {
      await updateResource(auth.token, 'portal/student/change-password', '', { current_password: curPwd, new_password: newPwd })
      toast.success('Password changed')
      setCurPwd('')
      setNewPwd('')
    } catch (err) {
      toast.error('Password change failed')
    }
  }

  if (loading) {
    return (
      <StudentLayout title="My Profile">
        <div className="skeleton-grid"><div className="skeleton-card" style={{ height: 200 }} /></div>
      </StudentLayout>
    )
  }

  return (
    <StudentLayout title="My Profile">
      <div className="card" style={{ maxWidth: 600 }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 16, marginBottom: 20 }}>
          {profile?.photo_path ? (
            <img src={`http://127.0.0.1:8000/${profile.photo_path}`} alt="" style={{ width: 80, height: 80, borderRadius: '50%', objectFit: 'cover' }} />
          ) : (
            <div style={{ width: 80, height: 80, borderRadius: '50%', background: '#e2e8f0', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: 24 }}>👤</div>
          )}
          <div>
            <h3>{profile?.full_name}</h3>
            <p>{profile?.email}</p>
            <label className="btn btn-sm" style={{ cursor: 'pointer' }}>
              Upload Photo
              <input type="file" accept="image/*" onChange={handlePhoto} style={{ display: 'none' }} />
            </label>
          </div>
        </div>

        <div className="form-grid">
          <label>Admission No <input className="input" value={profile?.admission_no || ''} disabled /></label>
          <label>Class <input className="input" value={profile?.class_name || ''} disabled /></label>
          <label>Section <input className="input" value={profile?.section_name || ''} disabled /></label>
          <label>Gender <input className="input" value={profile?.gender || ''} disabled /></label>
          <label>DOB <input className="input" value={profile?.dob || ''} disabled /></label>
          <label>Status <input className="input" value={profile?.status || ''} disabled /></label>
          <label>
            Full Name
            <input className="input" value={fullName} onChange={(e) => setFullName(e.target.value)} disabled={!editing} />
          </label>
        </div>
        <div className="form-actions">
          {editing ? (
            <>
              <button className="btn btn-primary" onClick={handleUpdate}>Save</button>
              <button className="btn" onClick={() => setEditing(false)}>Cancel</button>
            </>
          ) : (
            <button className="btn" onClick={() => setEditing(true)}>Edit Profile</button>
          )}
        </div>
      </div>

      <div className="card" style={{ maxWidth: 600, marginTop: 20 }}>
        <h3>Change Password</h3>
        <div className="form-grid">
          <label>Current Password <input className="input" type="password" value={curPwd} onChange={(e) => setCurPwd(e.target.value)} /></label>
          <label>New Password <input className="input" type="password" value={newPwd} onChange={(e) => setNewPwd(e.target.value)} /></label>
        </div>
        <button className="btn btn-primary" onClick={handleChangePassword}>Change Password</button>
      </div>
    </StudentLayout>
  )
}
