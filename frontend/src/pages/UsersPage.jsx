import React, { useEffect, useState } from 'react'
import PageWrapper from '../components/PageWrapper'
import { useAuth } from '../hooks/useAuth.jsx'
import { listResources, createResource, updateResource, deleteResource } from '../api'
import toast from 'react-hot-toast'

export default function UsersPage() {
  const auth = useAuth()
  const [users, setUsers] = useState([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [form, setForm] = useState({ email: '', full_name: '', role: 'Student', password: '' })
  const [search, setSearch] = useState('')
  const [page, setPage] = useState(0)
  const pageSize = 10

  useEffect(() => { loadUsers() }, [page, search])

  const buildQuery = () => {
    const params = new URLSearchParams({ skip: page * pageSize, limit: pageSize })
    if (search) params.set('query', search)
    return params.toString()
  }

  const loadUsers = async () => {
    setLoading(true); setError('')
    try { const data = await listResources(auth.token, 'users', buildQuery()); setUsers(data) }
    catch (err) { setError(err.message) } finally { setLoading(false) }
  }

  const handleCreate = async (event) => {
    event.preventDefault(); setError('')
    const toastId = toast.loading('Creating user...')
    try {
      await createResource(auth.token, 'users', form)
      toast.success('User created!', { id: toastId })
      setForm({ email: '', full_name: '', role: 'Student', password: '' })
      await loadUsers()
    } catch (err) { setError(err.message); toast.error(err.message, { id: toastId }) }
  }

  const handleDelete = async (id) => {
    if (!window.confirm('Delete this user?')) return
    try { await deleteResource(auth.token, 'users', id); toast.success('User deleted'); await loadUsers() }
    catch (err) { toast.error(err.message) }
  }

  return (
    <PageWrapper title="User Management">
      <div className="card" style={{ marginBottom: 24 }}>
        <h2>Create User</h2>
        <form onSubmit={handleCreate} className="form-grid">
          <input className="input" value={form.email} onChange={(e) => setForm({ ...form, email: e.target.value })} placeholder="Email" required />
          <input className="input" value={form.full_name} onChange={(e) => setForm({ ...form, full_name: e.target.value })} placeholder="Full name" />
          <select className="input" value={form.role} onChange={(e) => setForm({ ...form, role: e.target.value })}>
            <option value="Student">Student</option><option value="Teacher">Teacher</option><option value="Parent">Parent</option>
            <option value="School Admin">School Admin</option><option value="Super Admin">Super Admin</option>
          </select>
          <input className="input" type="password" value={form.password} onChange={(e) => setForm({ ...form, password: e.target.value })} placeholder="Password" required />
          <div className="form-actions"><button className="btn btn-primary" type="submit">Create</button></div>
        </form>
      </div>
      <div className="card">
        <div className="list-header">
          <h2>Existing Users</h2>
          <input className="input search-input" placeholder="Search..." value={search} onChange={(e) => { setSearch(e.target.value); setPage(0) }} />
        </div>
        {loading ? (
          <div className="skeleton-list">{Array.from({ length: 5 }).map((_, i) => <div key={i} className="skeleton-row" />)}</div>
        ) : users.length === 0 ? (
          <div className="empty-state">No users found.</div>
        ) : (
          <div className="table-responsive">
            <table className="data-table">
              <thead><tr><th>ID</th><th>Email</th><th>Name</th><th>Role</th><th>Active</th><th>Actions</th></tr></thead>
              <tbody>
                {users.map((user) => (
                  <tr key={user.id}>
                    <td>{user.id}</td><td>{user.email}</td><td>{user.full_name}</td>
                    <td><span className="role-badge">{user.role}</span></td>
                    <td><span className="role-badge">{String(user.is_active)}</span></td>
                    <td className="action-cell"><button className="btn btn-sm btn-danger" onClick={() => handleDelete(user.id)}>Delete</button></td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
        <div className="pagination">
          <button className="btn btn-sm" disabled={page === 0} onClick={() => setPage(page - 1)}>Previous</button>
          <span>Page {page + 1}</span>
          <button className="btn btn-sm" disabled={users.length < pageSize} onClick={() => setPage(page + 1)}>Next</button>
        </div>
      </div>
      {error && <div className="error-banner">{error}</div>}
    </PageWrapper>
  )
}
