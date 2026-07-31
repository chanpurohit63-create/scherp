import React, { useEffect, useState } from 'react'
import SuperAdminLayout from '../components/SuperAdminLayout'
import { useAuth } from '../hooks/useAuth.jsx'
import { listResources, createResource, getResource, updateResource, BACKEND_URL } from '../api'
import toast from 'react-hot-toast'

const PAGE_SIZE = 10

export default function SuperAdminSchoolsPage() {
  const auth = useAuth()
  const [schools, setSchools] = useState([])
  const [loading, setLoading] = useState(true)
  const [search, setSearch] = useState('')
  const [statusFilter, setStatusFilter] = useState('')
  const [currentPage, setCurrentPage] = useState(1)
  const [showCreateModal, setShowCreateModal] = useState(false)
  const [showDetailsModal, setShowDetailsModal] = useState(null)
  const [showEditModal, setShowEditModal] = useState(null)
  const [editForm, setEditForm] = useState({})
  const [createdCredentials, setCreatedCredentials] = useState(null)
  const [form, setForm] = useState({ school_name: '', school_code: '', address: '', phone: '', email: '', subscription_plan: 'free', admin_email: '', admin_password: '', admin_name: '' })

  useEffect(() => { 
    setCurrentPage(1)
    loadSchools() 
  }, [search, statusFilter])

  const loadSchools = async () => {
    setLoading(true)
    try {
      const params = new URLSearchParams()
      if (search) params.append('search', search)
      if (statusFilter) params.append('status_filter', statusFilter)
      const query = params.toString()
      const data = await listResources(auth.token, `superadmin/schools?skip=0&limit=1000${query ? '&' + query : ''}`)
      setSchools(data)
    } catch (err) {
      console.error(err)
      toast.error('Failed to load schools')
    } finally {
      setLoading(false)
    }
  }

  // Pagination
  const totalPages = Math.ceil(schools.length / PAGE_SIZE)
  const paginatedSchools = schools.slice((currentPage - 1) * PAGE_SIZE, currentPage * PAGE_SIZE)

  const handleCreate = async (e) => {
    e.preventDefault()
    try {
      const school = await createResource(auth.token, 'superadmin/schools', {
        school_name: form.school_name,
        school_code: form.school_code,
        address: form.address,
        phone: form.phone,
        email: form.email,
        subscription_plan: form.subscription_plan,
      })
      
      if (form.admin_email && form.admin_password) {
        try {
          const response = await fetch(`${BACKEND_URL}/auth/register?school_id=${school.id}`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
              email: form.admin_email,
              password: form.admin_password,
              full_name: form.admin_name || form.school_name + ' Admin',
              role: 'School Admin',
            }),
          })
          if (response.ok) {
            setCreatedCredentials({ school: school.school_name, email: form.admin_email, password: form.admin_password })
          }
        } catch (err) {
          console.error('Failed to create admin user:', err)
        }
      }
      
      toast.success('School created successfully!')
      setShowCreateModal(false)
      setForm({ school_name: '', school_code: '', address: '', phone: '', email: '', subscription_plan: 'free', admin_email: '', admin_password: '', admin_name: '' })
      loadSchools()
    } catch (err) {
      toast.error(err.message || 'Failed to create school')
    }
  }

  const handleStatusChange = async (schoolId, newStatus) => {
    try {
      const action = newStatus === 'active' ? 'activate' : newStatus === 'suspended' ? 'suspend' : null
      if (action) {
        await createResource(auth.token, `superadmin/schools/${schoolId}/${action}`, {})
      } else {
        await createResource(auth.token, `superadmin/schools/${schoolId}`, { status: newStatus })
      }
      toast.success(`School ${newStatus} successfully`)
      loadSchools()
    } catch (err) {
      toast.error(err.message || 'Failed to update school')
    }
  }

  const handleResetPassword = async (schoolId, schoolName) => {
    const newPassword = prompt(`Enter new password for ${schoolName}'s admin:`)
    if (!newPassword) return
    try {
      await fetch(`${BACKEND_URL}/api/superadmin/schools/${schoolId}/reset-admin-password?new_password=${encodeURIComponent(newPassword)}`, {
        method: 'POST',
        headers: { Authorization: `Bearer ${auth.token}` },
      })
      toast.success('Password reset successfully')
    } catch (err) {
      toast.error(err.message || 'Failed to reset password')
    }
  }

  const handleEdit = (school) => {
    setEditForm({ ...school })
    setShowEditModal(school)
  }

  const handleSaveEdit = async (e) => {
    e.preventDefault()
    try {
      await updateResource(auth.token, 'superadmin/schools', editForm.id, {
        school_name: editForm.school_name,
        email: editForm.email,
        phone: editForm.phone,
        address: editForm.address,
        principal_name: editForm.principal_name,
        subscription_plan: editForm.subscription_plan,
      })
      toast.success('School updated successfully!')
      setShowEditModal(null)
      loadSchools()
    } catch (err) {
      toast.error(err.message || 'Failed to update school')
    }
  }

  const handleViewDetails = async (schoolId) => {
    try {
      const details = await getResource(auth.token, 'superadmin/schools', schoolId)
      setShowDetailsModal(details)
    } catch (err) {
      toast.error('Failed to load school details')
    }
  }

  const getStatusBadge = (status) => {
    const map = {
      active: 'badge badge-success',
      inactive: 'badge badge-gray',
      suspended: 'badge badge-danger',
      expired: 'badge badge-warning',
      deleted: 'badge badge-danger',
    }
    return <span className={map[status] || 'badge badge-gray'}>{status}</span>
  }

  const getPlanBadge = (plan) => {
    const map = {
      free: 'badge badge-gray',
      basic: 'badge badge-info',
      standard: 'badge badge-primary',
      premium: 'badge badge-purple',
    }
    return <span className={map[plan] || 'badge badge-gray'}>{plan || 'free'}</span>
  }

  if (loading) {
    return (
      <SuperAdminLayout title="Schools" breadcrumbs={[{ label: 'Schools', to: null }]}>
        <div className="skeleton-list">
          {Array.from({ length: 8 }).map((_, i) => <div key={i} className="skeleton-row" />)}
        </div>
      </SuperAdminLayout>
    )
  }

  return (
    <SuperAdminLayout title="Schools" breadcrumbs={[{ label: 'Schools', to: null }]}>
      <div className="table-container">
        <div className="table-header">
          <h3>All Schools</h3>
          <div className="table-toolbar">
            <input
              className="input search-input"
              placeholder="Search schools..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
            />
            <select className="input" style={{ width: 140 }} value={statusFilter} onChange={(e) => setStatusFilter(e.target.value)}>
              <option value="">All Status</option>
              <option value="active">Active</option>
              <option value="inactive">Inactive</option>
              <option value="suspended">Suspended</option>
              <option value="expired">Expired</option>
            </select>
            <button className="btn btn-primary" onClick={() => setShowCreateModal(true)}>+ New School</button>
          </div>
        </div>
        <div className="table-responsive">
          <table className="data-table">
            <thead>
              <tr>
                <th>School Name</th>
                <th>Code</th>
                <th>Status</th>
                <th>Plan</th>
                <th>Phone</th>
                <th>Email</th>
                <th>Created</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {paginatedSchools.length === 0 ? (
                <tr>
                  <td colSpan={8}>
                    <div className="empty-state">
                      <div className="empty-state-icon">🏫</div>
                      <h3>No schools found</h3>
                      <p>Get started by creating your first school.</p>
                    </div>
                  </td>
                </tr>
              ) : paginatedSchools.map((school) => (
                <tr key={school.id}>
                  <td><strong>{school.school_name}</strong></td>
                  <td><code>{school.school_code}</code></td>
                  <td>{getStatusBadge(school.status)}</td>
                  <td>{getPlanBadge(school.subscription_plan)}</td>
                  <td>{school.phone || '-'}</td>
                  <td>{school.email || '-'}</td>
                  <td>{school.created_on ? new Date(school.created_on).toLocaleDateString() : '-'}</td>
                  <td>
                    <div className="action-cell">
                      <button className="btn btn-sm btn-ghost" onClick={() => handleViewDetails(school.id)} title="View Details">👁️</button>
                      <button className="btn btn-sm btn-ghost" onClick={() => handleEdit(school)} title="Edit">✏️</button>
                      <button className="btn btn-sm btn-ghost" onClick={() => handleResetPassword(school.id, school.school_name)} title="Reset Password">🔑</button>
                      {school.status === 'active' && (
                        <button className="btn btn-sm btn-warning" onClick={() => handleStatusChange(school.id, 'suspended')}>Suspend</button>
                      )}
                      {school.status === 'suspended' && (
                        <button className="btn btn-sm btn-success" onClick={() => handleStatusChange(school.id, 'active')}>Activate</button>
                      )}
                      {school.status !== 'deleted' && school.status !== 'active' && (
                        <button className="btn btn-sm btn-primary" onClick={() => handleStatusChange(school.id, 'active')}>Activate</button>
                      )}
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        <div className="table-footer">
          <span className="pagination-info">
            Showing {(currentPage - 1) * PAGE_SIZE + 1}-{Math.min(currentPage * PAGE_SIZE, schools.length)} of {schools.length}
          </span>
          {totalPages > 1 && (
            <div className="pagination">
              <button onClick={() => setCurrentPage(1)} disabled={currentPage === 1}>«</button>
              <button onClick={() => setCurrentPage(currentPage - 1)} disabled={currentPage === 1}>‹</button>
              {Array.from({ length: totalPages }, (_, i) => i + 1)
                .filter(p => p === 1 || p === totalPages || Math.abs(p - currentPage) <= 2)
                .map((p) => (
                  <button key={p} className={currentPage === p ? 'active' : ''} onClick={() => setCurrentPage(p)}>
                    {p}
                  </button>
                ))}
              <button onClick={() => setCurrentPage(currentPage + 1)} disabled={currentPage === totalPages}>›</button>
              <button onClick={() => setCurrentPage(totalPages)} disabled={currentPage === totalPages}>»</button>
            </div>
          )}
        </div>
      </div>

      {/* Create Modal */}
      {showCreateModal && (
        <div className="modal-overlay" onClick={() => setShowCreateModal(false)}>
          <div className="modal" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h2>Create New School</h2>
              <button className="modal-close" onClick={() => setShowCreateModal(false)}>✕</button>
            </div>
            <form onSubmit={handleCreate}>
              <div className="modal-body">
                <div className="form-section">
                  <div className="form-section-title">School Details</div>
                  <div className="form-grid">
                    <div className="form-group">
                      <label>School Name *</label>
                      <input className="input" required value={form.school_name} onChange={(e) => setForm({ ...form, school_name: e.target.value })} />
                    </div>
                    <div className="form-group">
                      <label>School Code *</label>
                      <input className="input" required value={form.school_code} onChange={(e) => setForm({ ...form, school_code: e.target.value.toUpperCase() })} placeholder="e.g. INT-001" />
                    </div>
                    <div className="form-group">
                      <label>Phone</label>
                      <input className="input" value={form.phone} onChange={(e) => setForm({ ...form, phone: e.target.value })} />
                    </div>
                    <div className="form-group">
                      <label>Email</label>
                      <input className="input" type="email" value={form.email} onChange={(e) => setForm({ ...form, email: e.target.value })} />
                    </div>
                    <div className="form-group" style={{ gridColumn: 'span 2' }}>
                      <label>Address</label>
                      <textarea className="input" value={form.address} onChange={(e) => setForm({ ...form, address: e.target.value })} />
                    </div>
                    <div className="form-group">
                      <label>Subscription Plan</label>
                      <select className="input" value={form.subscription_plan} onChange={(e) => setForm({ ...form, subscription_plan: e.target.value })}>
                        <option value="free">Free</option>
                        <option value="basic">Basic</option>
                        <option value="standard">Standard</option>
                        <option value="premium">Premium</option>
                      </select>
                    </div>
                  </div>
                </div>
                <div className="form-section">
                  <div className="form-section-title">School Admin Account</div>
                  <div className="alert alert-info">
                    A School Admin account will be created automatically. The admin will be prompted to change their password on first login.
                  </div>
                  <div className="form-grid">
                    <div className="form-group">
                      <label>Admin Name</label>
                      <input className="input" value={form.admin_name} onChange={(e) => setForm({ ...form, admin_name: e.target.value })} placeholder="e.g. John Smith" />
                    </div>
                    <div className="form-group">
                      <label>Admin Email *</label>
                      <input className="input" type="email" required value={form.admin_email} onChange={(e) => setForm({ ...form, admin_email: e.target.value })} placeholder="admin@school.com" />
                    </div>
                    <div className="form-group" style={{ gridColumn: 'span 2' }}>
                      <label>Temporary Password *</label>
                      <input className="input" required value={form.admin_password} onChange={(e) => setForm({ ...form, admin_password: e.target.value })} placeholder="Temporary password" />
                    </div>
                  </div>
                </div>
              </div>
              <div className="modal-footer">
                <button type="button" className="btn" onClick={() => setShowCreateModal(false)}>Cancel</button>
                <button type="submit" className="btn btn-primary">Create School</button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* View Details Modal */}
      {showDetailsModal && (
        <div className="modal-overlay" onClick={() => setShowDetailsModal(null)}>
          <div className="modal" onClick={(e) => e.stopPropagation()} style={{ maxWidth: 600 }}>
            <div className="modal-header">
              <h2>{showDetailsModal.school_name}</h2>
              <button className="modal-close" onClick={() => setShowDetailsModal(null)}>✕</button>
            </div>
            <div className="modal-body">
              <div className="form-grid">
                <div className="form-group">
                  <label>School Code</label>
                  <div style={{ padding: '10px 14px', background: '#f8fafc', borderRadius: 8 }}><code>{showDetailsModal.school_code}</code></div>
                </div>
                <div className="form-group">
                  <label>Status</label>
                  <div style={{ padding: '10px 14px' }}>{getStatusBadge(showDetailsModal.status)}</div>
                </div>
                <div className="form-group">
                  <label>Plan</label>
                  <div style={{ padding: '10px 14px' }}>{getPlanBadge(showDetailsModal.subscription_plan)}</div>
                </div>
                <div className="form-group">
                  <label>Phone</label>
                  <div style={{ padding: '10px 14px', background: '#f8fafc', borderRadius: 8 }}>{showDetailsModal.phone || '-'}</div>
                </div>
                <div className="form-group" style={{ gridColumn: 'span 2' }}>
                  <label>Email</label>
                  <div style={{ padding: '10px 14px', background: '#f8fafc', borderRadius: 8 }}>{showDetailsModal.email || '-'}</div>
                </div>
                <div className="form-group" style={{ gridColumn: 'span 2' }}>
                  <label>Address</label>
                  <div style={{ padding: '10px 14px', background: '#f8fafc', borderRadius: 8 }}>{showDetailsModal.address || '-'}</div>
                </div>
                <div className="form-group">
                  <label>Principal</label>
                  <div style={{ padding: '10px 14px', background: '#f8fafc', borderRadius: 8 }}>{showDetailsModal.principal_name || '-'}</div>
                </div>
                <div className="form-group">
                  <label>Created</label>
                  <div style={{ padding: '10px 14px', background: '#f8fafc', borderRadius: 8 }}>{showDetailsModal.created_on ? new Date(showDetailsModal.created_on).toLocaleString() : '-'}</div>
                </div>
                {showDetailsModal.subscription_start && (
                  <div className="form-group">
                    <label>Subscription Start</label>
                    <div style={{ padding: '10px 14px', background: '#f8fafc', borderRadius: 8 }}>{new Date(showDetailsModal.subscription_start).toLocaleDateString()}</div>
                  </div>
                )}
                {showDetailsModal.subscription_end && (
                  <div className="form-group">
                    <label>Subscription End</label>
                    <div style={{ padding: '10px 14px', background: '#f8fafc', borderRadius: 8 }}>{new Date(showDetailsModal.subscription_end).toLocaleDateString()}</div>
                  </div>
                )}
              </div>
            </div>
            <div className="modal-footer">
              <button className="btn" onClick={() => setShowDetailsModal(null)}>Close</button>
              <button className="btn btn-primary" onClick={() => { setShowDetailsModal(null); handleEdit(showDetailsModal) }}>Edit School</button>
            </div>
          </div>
        </div>
      )}

      {/* Edit Modal */}
      {showEditModal && (
        <div className="modal-overlay" onClick={() => setShowEditModal(null)}>
          <div className="modal" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h2>Edit School</h2>
              <button className="modal-close" onClick={() => setShowEditModal(null)}>✕</button>
            </div>
            <form onSubmit={handleSaveEdit}>
              <div className="modal-body">
                <div className="form-grid">
                  <div className="form-group" style={{ gridColumn: 'span 2' }}>
                    <label>School Name *</label>
                    <input className="input" required value={editForm.school_name || ''} onChange={(e) => setEditForm({ ...editForm, school_name: e.target.value })} />
                  </div>
                  <div className="form-group">
                    <label>Phone</label>
                    <input className="input" value={editForm.phone || ''} onChange={(e) => setEditForm({ ...editForm, phone: e.target.value })} />
                  </div>
                  <div className="form-group">
                    <label>Email</label>
                    <input className="input" type="email" value={editForm.email || ''} onChange={(e) => setEditForm({ ...editForm, email: e.target.value })} />
                  </div>
                  <div className="form-group" style={{ gridColumn: 'span 2' }}>
                    <label>Address</label>
                    <textarea className="input" value={editForm.address || ''} onChange={(e) => setEditForm({ ...editForm, address: e.target.value })} />
                  </div>
                  <div className="form-group">
                    <label>Principal Name</label>
                    <input className="input" value={editForm.principal_name || ''} onChange={(e) => setEditForm({ ...editForm, principal_name: e.target.value })} />
                  </div>
                  <div className="form-group">
                    <label>Subscription Plan</label>
                    <select className="input" value={editForm.subscription_plan || 'free'} onChange={(e) => setEditForm({ ...editForm, subscription_plan: e.target.value })}>
                      <option value="free">Free</option>
                      <option value="basic">Basic</option>
                      <option value="standard">Standard</option>
                      <option value="premium">Premium</option>
                    </select>
                  </div>
                </div>
              </div>
              <div className="modal-footer">
                <button type="button" className="btn" onClick={() => setShowEditModal(null)}>Cancel</button>
                <button type="submit" className="btn btn-primary">Save Changes</button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Credentials Modal */}
      {createdCredentials && (
        <div className="modal-overlay" onClick={() => setCreatedCredentials(null)}>
          <div className="modal" onClick={(e) => e.stopPropagation()} style={{ maxWidth: 480 }}>
            <div className="modal-header">
              <h2>✅ School Created!</h2>
              <button className="modal-close" onClick={() => setCreatedCredentials(null)}>✕</button>
            </div>
            <div className="modal-body">
              <div className="alert alert-success">
                School and admin account created successfully! Share these credentials with the school admin.
              </div>
              <div style={{ background: '#f8fafc', padding: 20, borderRadius: 8, marginTop: 16 }}>
                <div style={{ marginBottom: 12 }}>
                  <div style={{ fontSize: '0.8rem', color: '#64748b', marginBottom: 4 }}>School</div>
                  <div style={{ fontWeight: 600 }}>{createdCredentials.school}</div>
                </div>
                <div style={{ marginBottom: 12 }}>
                  <div style={{ fontSize: '0.8rem', color: '#64748b', marginBottom: 4 }}>Admin Email</div>
                  <div style={{ fontWeight: 600 }}>{createdCredentials.email}</div>
                </div>
                <div>
                  <div style={{ fontSize: '0.8rem', color: '#64748b', marginBottom: 4 }}>Temporary Password</div>
                  <div style={{ fontWeight: 600, fontFamily: 'monospace' }}>{createdCredentials.password}</div>
                </div>
              </div>
            </div>
            <div className="modal-footer">
              <button className="btn btn-primary" onClick={() => setCreatedCredentials(null)}>Done</button>
            </div>
          </div>
        </div>
      )}
    </SuperAdminLayout>
  )
}