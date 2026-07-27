import React from 'react'
import { Link } from 'react-router-dom'
import PageWrapper from '../components/PageWrapper'
import { useAuth } from '../hooks/useAuth'

export default function DashboardPage() {
  const auth = useAuth()

  return (
    <PageWrapper title="Dashboard">
      <div style={{ marginBottom: 24 }}>
        <p>Welcome, {auth.profile?.full_name || auth.profile?.email}.</p>
        <p>Role: {auth.profile?.role}</p>
      </div>
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: 16 }}>
        <Link to="/users" style={cardStyle}>User Management</Link>
        <Link to="/students" style={cardStyle}>Students</Link>
        <Link to="/teachers" style={cardStyle}>Teachers</Link>
        <Link to="/attendance" style={cardStyle}>Attendance</Link>
        <Link to="/exams" style={cardStyle}>Exams</Link>
        <Link to="/fees" style={cardStyle}>Fees</Link>
        <Link to="/notices" style={cardStyle}>Notices</Link>
      </div>
    </PageWrapper>
  )
}

const cardStyle = {
  display: 'block',
  padding: 16,
  border: '1px solid #ddd',
  borderRadius: 8,
  textDecoration: 'none',
  color: '#111',
  background: '#fafafa',
}
