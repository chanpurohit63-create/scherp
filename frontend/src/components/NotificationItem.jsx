import React from 'react'

const CATEGORY_ICONS = {
  Academic: '📚',
  Homework: '📝',
  Attendance: '📋',
  Examinations: '📝',
  Fees: '💰',
  Payments: '💳',
  Messages: '💬',
  Events: '🎉',
  Certificates: '🎓',
  Documents: '📄',
  Security: '🔒',
  System: '⚙️',
  Announcements: '📢',
}

const PRIORITY_COLORS = {
  low: '#6b7280',
  normal: '#3b82f6',
  high: '#f59e0b',
  critical: '#ef4444',
}

function getRelativeTime(dateString) {
  const now = new Date()
  const date = new Date(dateString)
  const diffMs = now - date
  const diffSecs = Math.floor(diffMs / 1000)
  const diffMins = Math.floor(diffSecs / 60)
  const diffHours = Math.floor(diffMins / 60)
  const diffDays = Math.floor(diffHours / 24)

  if (diffSecs < 60) return 'just now'
  if (diffMins < 60) return `${diffMins}m ago`
  if (diffHours < 24) return `${diffHours}h ago`
  if (diffDays < 7) return `${diffDays}d ago`
  return date.toLocaleDateString()
}

export default function NotificationItem({
  notification,
  onMarkRead,
  onDelete,
  onArchive,
  onPin,
  onClick,
}) {
  const icon = CATEGORY_ICONS[notification.category] || '🔔'
  const priorityColor = PRIORITY_COLORS[notification.priority] || '#6b7280'

  const handleClick = () => {
    if (!notification.is_read && onMarkRead) {
      onMarkRead(notification.id)
    }
    if (onClick) {
      onClick(notification)
    }
  }

  return (
    <div
      className={`notification-item ${!notification.is_read ? 'unread' : ''} ${notification.is_pinned ? 'pinned' : ''}`}
      onClick={handleClick}
      style={{
        borderLeft: `3px solid ${priorityColor}`,
        opacity: notification.is_archived ? 0.6 : 1,
      }}
    >
      <div className="notification-item-icon">{icon}</div>
      <div className="notification-item-content">
        <div className="notification-item-title">
          {notification.title}
          {notification.is_pinned && <span className="pin-indicator">📌</span>}
        </div>
        <div className="notification-item-message">{notification.message}</div>
        <div className="notification-item-meta">
          <span className="notification-item-time">{getRelativeTime(notification.created_on)}</span>
          {notification.category && (
            <span className="notification-item-category">{notification.category}</span>
          )}
          {notification.priority && notification.priority !== 'normal' && (
            <span className={`notification-item-priority ${notification.priority}`}>
              {notification.priority}
            </span>
          )}
        </div>
      </div>
      <div className="notification-item-actions">
        {!notification.is_read && (
          <button
            className="notification-action-btn"
            onClick={(e) => { e.stopPropagation(); onMarkRead?.(notification.id) }}
            title="Mark as read"
          >
            ✓
          </button>
        )}
        {onPin && (
          <button
            className="notification-action-btn"
            onClick={(e) => { e.stopPropagation(); onPin(notification.id) }}
            title={notification.is_pinned ? 'Unpin' : 'Pin'}
          >
            📌
          </button>
        )}
        {onArchive && (
          <button
            className="notification-action-btn"
            onClick={(e) => { e.stopPropagation(); onArchive(notification.id) }}
            title={notification.is_archived ? 'Restore' : 'Archive'}
          >
            {notification.is_archived ? '📤' : '📁'}
          </button>
        )}
        {onDelete && (
          <button
            className="notification-action-btn delete"
            onClick={(e) => { e.stopPropagation(); onDelete(notification.id) }}
            title="Delete"
          >
            🗑️
          </button>
        )}
      </div>
    </div>
  )
}
