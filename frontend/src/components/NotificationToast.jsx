import React, { useEffect, useState } from 'react'

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

export default function NotificationToast({ notification, onDismiss, onNavigate }) {
  const [visible, setVisible] = useState(false)
  const [exiting, setExiting] = useState(false)

  useEffect(() => {
    // Trigger entrance animation
    const enterTimer = setTimeout(() => setVisible(true), 100)
    // Auto dismiss after 5 seconds
    const dismissTimer = setTimeout(() => handleDismiss(), 5000)

    return () => {
      clearTimeout(enterTimer)
      clearTimeout(dismissTimer)
    }
  }, [notification.id])

  const handleDismiss = () => {
    setExiting(true)
    setTimeout(() => onDismiss(notification.id), 300)
  }

  const handleClick = () => {
    if (notification.related_module && onNavigate) {
      onNavigate(notification.related_module, notification.related_record_id)
    }
    handleDismiss()
  }

  const icon = CATEGORY_ICONS[notification.category] || '🔔'

  return (
    <div
      className={`notification-toast ${visible ? 'visible' : ''} ${exiting ? 'exiting' : ''}`}
      onClick={handleClick}
      style={{
        borderLeft: `4px solid ${
          notification.priority === 'critical' ? '#ef4444' :
          notification.priority === 'high' ? '#f59e0b' :
          notification.priority === 'low' ? '#6b7280' : '#3b82f6'
        }`,
      }}
    >
      <div className="notification-toast-icon">{icon}</div>
      <div className="notification-toast-content">
        <div className="notification-toast-title">{notification.title}</div>
        <div className="notification-toast-message">{notification.message}</div>
      </div>
      <button
        className="notification-toast-close"
        onClick={(e) => { e.stopPropagation(); handleDismiss() }}
      >
        ×
      </button>
    </div>
  )
}
