import React from 'react'

export default function EmptyState({
  icon = '📭',
  title = 'No data found',
  message = '',
  action = null,
  compact = false,
}) {
  return (
    <div className={`empty-state ${compact ? 'empty-state-compact' : ''}`}>
      <div className="empty-state-icon">{icon}</div>
      <h3>{title}</h3>
      {message && <p>{message}</p>}
      {action && <div className="empty-state-action">{action}</div>}
    </div>
  )
}