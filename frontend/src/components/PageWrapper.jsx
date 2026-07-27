import React from 'react'

export default function PageWrapper({ title, children }) {
  return (
    <div style={{ padding: 24, fontFamily: 'Arial, sans-serif' }}>
      <h1 style={{ marginBottom: 16 }}>{title}</h1>
      {children}
    </div>
  )
}
