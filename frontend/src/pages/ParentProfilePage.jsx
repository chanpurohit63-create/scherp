import React, { useEffect, useState } from 'react'
import ParentLayout from '../components/ParentLayout'
import { useAuth } from '../hooks/useAuth.jsx'
import { listResources, updateResource, uploadFile } from '../api'
import toast from 'react-hot-toast'

export default function ParentProfilePage() {
  const auth = useAuth()
  const [profile, setProfile] = useState(null)
  const [loading, setLoading] = useState(true)
  const [editMode, setEditMode] = useState(false)
  const [fullName, setFullName] = useState('')
  const [phone, setPhone] = useState('')
  const [address, setAddress] = useState('')

  useEffect(() => { loadProfile() }, [])

  const loadProfile = async () => {
    try {
      const d = await listResources(auth.token, 'portal/parent/profile')
      setProfile(d)
      setFullName(d.full_name || '')
      setPhone(d.phone || '')
      setAddress(d.address || '')
    } catch (err) { console.error(err) }
    finally { setLoading(false) }
  }

  const handleSave = async () => {
    try {
      await updateResource(auth.token, 'portal/parent/profile', 0, { full_name: fullName, phone, address })
      toast.success('Profile updated')
      setEditMode(false)
      loadProfile()
    } catch (err) { toast.error('Update failed') }
  }

  const handlePhoto = async (e) => {
    const file = e.target.files[0]
    if (!file) return
    try {
      await uploadFile(auth.token, 'portal/student/photo', file)
      toast.success('Photo uploaded')
    } catch (err) { toast.error('Upload failed') }
  }

  if (loading) {
    return <ParentLayout title="Profile"><div className="skeleton-card" style={{ height: 200 }} /></ParentLayout>
  }

  return (
    <ParentLayout title="Profile">
      <div className="card" style={{ maxWidth: 500 }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 16, marginBottom: 20 }}>
          <div style={{ position: 'relative' }}>
            <div style={{ width: 80, height: 80, borderRadius: '50%', background: '#e2e8f0', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: 32 }}>👤</div>
            <input type="file" accept="image/*" onChange={handlePhoto} style={{ position: 'absolute', top: 0, left: 0, width: 80, height: 80, opacity: 0, cursor: 'pointer' }} />
          </div>
          <div>
            <h3>{profile?.full_name}</h3>
            <p style={{ color: '#64748b', fontSize: '0.85rem' }}>{profile?.email}</p>
          </div>
        </div>

        {editMode ? (
          <div className="form-grid">
            <label>Full Name <input className="input" value={fullName} onChange={(e) => setFullName(e.target.value)} /></label>
            <label>Phone <input className="input" value={phone} onChange={(e) => setPhone(e.target.value)} /></label>
            <label>Address <textarea className="input" value={address} onChange={(e) => setAddress(e.target.value)} /></label>
            <div className="form-actions">
              <button className="btn btn-primary" onClick={handleSave}>Save</button>
              <button className="btn" onClick={() => setEditMode(false)}>Cancel</button>
            </div>
          </div>
        ) : (
          <div>
            <p><strong>Email:</strong> {profile?.email}</p>
            <p><strong>Phone:</strong> {profile?.phone || '-'}</p>
            <p><strong>Address:</strong> {profile?.address || '-'}</p>
            <button className="btn btn-primary" onClick={() => setEditMode(true)} style={{ marginTop: 12 }}>Edit Profile</button>
          </div>
        )}
      </div>
    </ParentLayout>
  )
}
