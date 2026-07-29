import React from 'react'

export default function NotificationBadge({ count, onClick, className = '' }) {
  if (count === 0 || count === undefined) return null

  return (
    <span
      className={`notification-badge ${className}`}
      onClick={onClick}
      title={`${count} unread notification${count !== 1 ? 's' : ''}`}
    >
      {count > 99 ? '99+' : count}
    </span>
  )
}
