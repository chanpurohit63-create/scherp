import React, { useEffect, useState } from 'react'
import PageWrapper from '../components/PageWrapper'
import { useAuth } from '../hooks/useAuth'
import { listResources, createResource, updateResource, deleteResource } from '../api'

export default function UsersPage() {
  const auth = useAuth()
  const [users, setUsers] = useState([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [form, setForm] = useState({ email: '', full_name: '', role: 'Student', password: '' })

  useEffect(() => {
    loadUsers()
  }, [])

  const loadUsers = async () => {
    setLoading(true)
    setError('')
    try {
      const data = await listResources(auth.token, 'users')
      setUsers(data)
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  const handleCreate = async (event) => {
    event.preventDefault()
    setError('')
    try {
      await createResource(auth.token, 'users', form)
      setForm({ email: '', full_name: '', role: 'Student', password: '' })
      await loadUsers()
    } catch (err) {
      setError(err.message)
    }
  }

  const handleDelete = async (id) => {
    if (!window.confirm('Delete this user?')) return
    try {
      await deleteResource(auth.token, 'users', id)
      await loadUsers()
    } catch (err) {
      setError(err.message)
    }
  }

  return (
    <PageWrapper title="User Management">
      <section style={{ marginBottom: 24 }}>
        <h2>Create User</h2>
        <form onSubmit={handleCreate} style={{ display: 'grid', gap: 12, maxWidth: 520 }}>
          <input value={form.email} onChange={(e) => setForm({ ...form, email: e.target.value })} placeholder="Email" required />
          <input value={form.full_name} onChange={(e) => setForm({ ...form, full_name: e.target.value })} placeholder="Full name" />
          <select value={form.role} onChange={(e) => setForm({ ...form, role: e.target.value })}>
            <option value="Student">Student</option>
            <option value="Teacher">Teacher</option>
            <option value="Parent">Parent</option>
            <option value="School Admin">School Admin</option>
            <option value="Super Admin">Super Admin</option>
          </select>
          <input type="password" value={form.password} onChange={(e) => setForm({ ...form, password: e.target.value })} placeholder="Password" required />
          <button type="submit" style={{ padding: '10px 16px' }}>Create</button>
        </form>
      </section>

      <section>
        <h2>Existing Users</h2>
        {loading ? (
          <p>Loading users...</p>
        ) : (
          <table style={{ width: '100%', borderCollapse: 'collapse' }}>
            <thead>
              <tr>
                <th style={thStyle}>ID</th>
                <th style={thStyle}>Email</th>
                <th style={thStyle}>Name</th>
                <th style={thStyle}>Role</th>
                <th style={thStyle}>Active</th>
                <th style={thStyle}>Actions</th>
              </tr>
            </thead>
            <tbody>
              {users.map((user) => (
                <tr key={user.id}>
                  <td style={tdStyle}>{user.id}</td>
                  <td style={tdStyle}>{user.email}</td>
                  <td style={tdStyle}>{user.full_name}</td>
                  <td style={tdStyle}>{user.role}</td>
                  <td style={tdStyle}>{String(user.is_active)}</td>
                  <td style={tdStyle}>
                    <button onClick={() => handleDelete(user.id)} style={{ padding: '6px 10px' }}>Delete</button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </section>

      {error && <p style={{ color: 'red' }}>{error}</p>}
    </PageWrapper>
  )
}

const thStyle = { borderBottom: '1px solid #ddd', padding: 8, textAlign: 'left' }
const tdStyle = { borderBottom: '1px solid #eee', padding: 8 }
